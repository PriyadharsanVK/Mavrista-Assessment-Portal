#!/usr/bin/env python3
"""Assessment Portal API and static web server (Python standard library only)."""
from __future__ import annotations

import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import sys
import time
import subprocess
import tempfile
import threading
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('ASSESSMENT_DATA_DIR', ROOT / 'data')).resolve()
DB_PATH = DATA_DIR / 'assessment.sqlite3'
HOST = os.environ.get('ASSESSMENT_HOST', '127.0.0.1')
PORT = int(os.environ.get('ASSESSMENT_PORT', '8000'))
SESSION_HOURS = int(os.environ.get('ASSESSMENT_SESSION_HOURS', '12'))
SESSION_IDLE_MINUTES = int(os.environ.get('ASSESSMENT_SESSION_IDLE_MINUTES', '30'))
COOKIE_SECURE = os.environ.get('ASSESSMENT_COOKIE_SECURE', '0') == '1'
TZ_IST = timezone(timedelta(hours=5, minutes=30), name='IST')
SUPPORTED_LANGUAGES = {'Java', 'Python', 'JavaScript', 'C++', 'C'}
ID_RE = re.compile(r'^[A-Za-z0-9_.-]{2,48}$')
LOGIN_ATTEMPTS: dict[str, list[float]] = {}

SCHEMA = '''
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS system_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY, role TEXT NOT NULL CHECK(role IN ('admin','student')),
  name TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE,
  password_hash TEXT NOT NULL, domain_id INTEGER REFERENCES domains(id),
  status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Disabled')),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS domains (
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE COLLATE NOCASE,
  category TEXT NOT NULL CHECK(category IN ('Software','Electrical / Electronics')),
  description TEXT NOT NULL DEFAULT '', icon TEXT NOT NULL DEFAULT '◈',
  status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Archived')),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS questions (
  id TEXT PRIMARY KEY, domain_id INTEGER NOT NULL REFERENCES domains(id),
  type TEXT NOT NULL CHECK(type IN ('MCQ','Coding')), title TEXT NOT NULL,
  difficulty TEXT NOT NULL CHECK(difficulty IN ('Easy','Medium','Hard')),
  data_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Published' CHECK(status IN ('Published','Archived')),
  version INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assessments (
  id TEXT PRIMARY KEY, domain_id INTEGER NOT NULL REFERENCES domains(id),
  title TEXT NOT NULL, starts_at TEXT NOT NULL, duration_min INTEGER NOT NULL CHECK(duration_min BETWEEN 5 AND 240),
  mcq_count INTEGER NOT NULL CHECK(mcq_count >= 0), coding_count INTEGER NOT NULL CHECK(coding_count >= 0),
  status TEXT NOT NULL DEFAULT 'Scheduled' CHECK(status IN ('Scheduled','Draft','Cancelled')),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  csrf_token TEXT NOT NULL, expires_at TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attempts (
  id TEXT PRIMARY KEY, assessment_id TEXT NOT NULL REFERENCES assessments(id),
  student_id TEXT NOT NULL REFERENCES users(id), started_at TEXT NOT NULL,
  deadline_at TEXT NOT NULL, submitted_at TEXT, submit_reason TEXT,
  visibility_events INTEGER NOT NULL DEFAULT 0, fullscreen_events INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'In progress' CHECK(status IN ('In progress','Submitted','Expired')),
  score INTEGER, max_score INTEGER, grading_status TEXT NOT NULL DEFAULT 'Not graded',
  UNIQUE(assessment_id, student_id)
);
CREATE TABLE IF NOT EXISTS attempt_questions (
  attempt_id TEXT NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
  question_id TEXT NOT NULL, ordinal INTEGER NOT NULL, snapshot_json TEXT NOT NULL, grading_json TEXT NOT NULL,
  PRIMARY KEY(attempt_id, question_id), UNIQUE(attempt_id, ordinal)
);
CREATE TABLE IF NOT EXISTS answers (
  attempt_id TEXT NOT NULL, question_id TEXT NOT NULL, answer_json TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(attempt_id, question_id),
  FOREIGN KEY(attempt_id, question_id) REFERENCES attempt_questions(attempt_id, question_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS review_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, attempt_id TEXT NOT NULL REFERENCES attempts(id),
  event_type TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
  reviewed_at TEXT, reviewed_by TEXT REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_questions_domain_type ON questions(domain_id,type,status);
CREATE INDEX IF NOT EXISTS idx_assessments_schedule ON assessments(domain_id,status,starts_at);
CREATE INDEX IF NOT EXISTS idx_attempts_student ON attempts(student_id,started_at);
'''

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def stamp(value: datetime | None = None) -> str:
    return (value or now_utc()).astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

def parse_instant(value: str) -> datetime:
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError('Provide a valid ISO date and time with a timezone.')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Date and time must include a timezone, such as +05:30 for IST.')
    return dt.astimezone(timezone.utc)

def db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    con.execute('PRAGMA journal_mode = WAL')
    return con

def init_db() -> None:
    with db() as con:
        con.executescript(SCHEMA)

def get_setting(key: str, default: str = '') -> str:
    try:
        con = db()
        row = con.execute('SELECT value FROM system_settings WHERE key=?', (key,)).fetchone()
        return row['value'] if row else default
    except sqlite3.OperationalError:
        return default

def set_setting(key: str, value: str) -> None:
    con = db()
    con.execute('INSERT INTO system_settings(key, value, updated_at) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at', (key, value, stamp()))

def get_sheets_url() -> str:
    return get_setting('sheets_webhook_url') or os.environ.get('SHEETS_WEBHOOK_URL', '').strip()

def post_to_sheets(payload: dict) -> bool:
    url = get_sheets_url()
    if not url:
        return False
    try:
        import urllib.request
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json', 'User-Agent': 'AssessmentPortal/1.0'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=35) as resp:
            return resp.status in (200, 302)
    except Exception as e:
        sys.stderr.write(f'[Sheets Sync Warning] {e}\n')
        return False

def sync_sheets_row(sheet: str, data: dict) -> None:
    url = get_sheets_url()
    if not url:
        return
    payload = {'action': 'append', 'sheet': sheet, 'data': data}
    threading.Thread(target=post_to_sheets, args=(payload,), daemon=True).start()

# ─── DATA RETENTION / CLEANUP ──────────────────────────────────────────────

RETENTION_DAYS_DEFAULT = 90  # default: delete old closed attempts after 90 days

def get_retention_days() -> int:
    try:
        return max(1, int(get_setting('retention_days', str(RETENTION_DAYS_DEFAULT))))
    except Exception:
        return RETENTION_DAYS_DEFAULT

def cleanup_old_data() -> dict:
    """Delete expired sessions and old completed/expired attempts older than retention period.
    Hidden test cases stay in the questions table (they are part of the question definition, not attempts).
    Only attempt rows, their answers, and review events older than the cut-off are removed."""
    days = get_retention_days()
    cutoff = stamp(now_utc() - timedelta(days=days))
    con = db()
    # 1. Remove expired login sessions
    s_del = con.execute("DELETE FROM sessions WHERE expires_at < ?", (cutoff,)).rowcount
    # 2. Remove review events linked to old closed attempts
    re_del = con.execute(
        """DELETE FROM review_events WHERE attempt_id IN (
            SELECT id FROM attempts WHERE status IN ('Submitted','Expired')
            AND coalesce(submitted_at, started_at) < ?
        )""", (cutoff,)).rowcount
    # 3. Remove old closed attempts (answers cascade via FK)
    a_del = con.execute(
        """DELETE FROM attempts WHERE status IN ('Submitted','Expired')
            AND coalesce(submitted_at, started_at) < ?""", (cutoff,)).rowcount
    return {'sessions': s_del, 'attempts': a_del, 'review_events': re_del, 'cutoff': cutoff, 'retention_days': days}

def _run_daily_cleanup():
    """Background thread: run cleanup on startup, then every 24 h."""
    import time as _time
    while True:
        try:
            result = cleanup_old_data()
            if any(v for k, v in result.items() if isinstance(v, int) and v > 0):
                sys.stdout.write(f'[Cleanup] Deleted: {result}\n')
        except Exception as e:
            sys.stderr.write(f'[Cleanup Error] {e}\n')
        _time.sleep(86400)  # wait 24 hours

def sync_sheets_all() -> dict:
    url = get_sheets_url()
    if not url:
        raise ApiError(400, 'Google Sheets Webhook URL is not configured. Set it in Sheets Sync settings.')
    con = db()
    domains = [dict(r) for r in con.execute('SELECT * FROM domains ORDER BY id').fetchall()]
    students = [dict(r) for r in con.execute('SELECT u.id, u.name, u.email, coalesce(d.name, "") domain, u.status, u.created_at FROM users u LEFT JOIN domains d ON d.id=u.domain_id WHERE u.role="student" ORDER BY u.name').fetchall()]
    raw_questions = con.execute('SELECT q.id, coalesce(d.name, "") domain, q.type, q.difficulty, q.title, q.data_json, q.status, q.created_at FROM questions q LEFT JOIN domains d ON d.id=q.domain_id ORDER BY q.created_at DESC').fetchall()
    questions = []
    for rq in raw_questions:
        qd = dict(rq)
        try:
            parsed = json.loads(qd.pop('data_json', '{}'))
        except Exception:
            parsed = {}
        if qd['type'] == 'MCQ':
            qd['options'] = ' | '.join(parsed.get('options', []))
            qd['correct_option'] = parsed.get('correctOption', '')
            qd['languages'] = ''
            qd['sample_tests'] = ''
            qd['hidden_tests'] = ''
            qd['time_limit_sec'] = ''
            qd['memory_limit_mb'] = ''
        else:
            qd['options'] = ''
            qd['correct_option'] = ''
            qd['languages'] = ', '.join(parsed.get('languages', []))
            qd['sample_tests'] = len(parsed.get('sampleTests', []))
            qd['hidden_tests'] = len(parsed.get('hiddenTests', []))
            qd['time_limit_sec'] = parsed.get('timeLimitSeconds', 3)
            qd['memory_limit_mb'] = parsed.get('memoryLimitMB', 256)
        questions.append(qd)
    assessments = [dict(r) for r in con.execute('SELECT a.id, a.title, coalesce(d.name, "") domain, a.starts_at, a.duration_min, a.mcq_count, a.coding_count, a.status FROM assessments a LEFT JOIN domains d ON d.id=a.domain_id ORDER BY a.starts_at').fetchall()]
    results = [dict(r) for r in con.execute('SELECT t.id, u.id student_id, u.name student, a.title assessment, coalesce(d.name, "") domain, t.score, t.max_score, t.status, t.started_at, t.submitted_at, t.submit_reason FROM attempts t JOIN users u ON u.id=t.student_id JOIN assessments a ON a.id=t.assessment_id LEFT JOIN domains d ON d.id=a.domain_id ORDER BY coalesce(t.submitted_at, t.started_at) DESC').fetchall()]

    payload = {
        'action': 'sync_all',
        'data': {
            'domains': domains,
            'students': students,
            'questions': questions,
            'assessments': assessments,
            'results': results
        }
    }
    ok = post_to_sheets(payload)
    if not ok:
        raise ApiError(502, 'Could not push data to Google Sheets. Verify your Google Apps Script Web App URL and deployment.')
    return {
        'ok': True,
        'counts': {
            'domains': len(domains),
            'students': len(students),
            'questions': len(questions),
            'assessments': len(assessments),
            'results': len(results)
        }
    }

def pull_sheets_all() -> dict:
    url = get_sheets_url()
    if not url:
        raise ApiError(400, 'Google Sheets Webhook URL is not configured. Set it in Sheets Sync settings.')
    try:
        import urllib.request
        full_url = url + ('&' if '?' in url else '?') + 'action=read_all'
        req = urllib.request.Request(
            full_url,
            headers={'User-Agent': 'AssessmentPortal/1.0', 'Accept': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=35) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        raise ApiError(502, f'Could not read from Google Sheets: {e}')

    if not isinstance(data, dict) or not data.get('ok'):
        raise ApiError(502, 'Google Sheets returned an invalid response.')

    con = db()
    counts = {'domains': 0, 'students': 0}

    for d in data.get('domains', []):
        name = str(d.get('Name') or '').strip()
        cat = str(d.get('Category') or 'Software').strip()
        if not name: continue
        con.execute('''INSERT INTO domains(name, category, description, icon, status, created_at)
            VALUES(?,?,?,?,?,?) ON CONFLICT(name) DO UPDATE SET category=excluded.category, status=excluded.status''',
            (name, cat, str(d.get('Description') or ''), str(d.get('Icon') or '◈'), str(d.get('Status') or 'Active'), str(d.get('Created At') or stamp())))
        counts['domains'] += 1

    for s in data.get('students', []):
        sid = str(s.get('Student ID') or s.get('id') or '').strip()
        name = str(s.get('Name') or '').strip()
        email = str(s.get('Email') or '').strip()
        dom_name = str(s.get('Domain') or '').strip()
        if not sid or not email or not name: continue
        dom = con.execute('SELECT id FROM domains WHERE name=? COLLATE NOCASE', (dom_name,)).fetchone()
        dom_id = dom['id'] if dom else None
        con.execute('''INSERT INTO users(id, role, name, email, password_hash, domain_id, status, created_at)
            VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name, email=excluded.email, domain_id=coalesce(excluded.domain_id, users.domain_id), status=excluded.status''',
            (sid, 'student', name, email, password_hash(f"{sid.lower()}@2026"), dom_id, str(s.get('Status') or 'Active'), str(s.get('Created At') or stamp())))
        counts['students'] += 1

    return {'ok': True, 'restored': counts}

def password_hash(password: str) -> str:
    if not isinstance(password, str) or len(password) < 6 or len(password) > 256:
        raise ValueError('Password must be between 6 and 256 characters.')
    salt = secrets.token_bytes(16)
    rounds = 310_000
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, rounds)
    return f'pbkdf2_sha256${rounds}${salt.hex()}${digest.hex()}'

def password_matches(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt_hex, digest_hex = encoded.split('$')
        if algorithm != 'pbkdf2_sha256':
            return False
        derived = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt_hex), int(rounds))
        return hmac.compare_digest(derived.hex(), digest_hex)
    except (ValueError, TypeError):
        return False

def safe_question(row: sqlite3.Row) -> dict:
    data = json.loads(row['data_json'])
    if row['type'] == 'MCQ':
        data.pop('correctOption', None)
        data.pop('correct_option', None)
    else:
        data.pop('hiddenTests', None)
        data.pop('hidden_tests', None)
    return {'id': row['id'], 'domainId': row['domain_id'], 'domain_id': row['domain_id'], 'type': row['type'],
            'title': row['title'], 'difficulty': row['difficulty'], 'status': row['status'],
            'version': row['version'], **data}

class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status, self.message = status, message

class Handler(BaseHTTPRequestHandler):
    server_version = 'AssessmentPortal/1.0'
    protocol_version = 'HTTP/1.1'

    def log_message(self, fmt, *args):
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))

    def send_json(self, status: int, value: dict, headers: dict | None = None):
        try:
            body = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Connection', 'close')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; media-src 'self' blob:; connect-src 'self' https://script.google.com https://script.googleusercontent.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
            for k, v in (headers or {}).items(): self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True
        except (ConnectionResetError, BrokenPipeError):
            pass

    def send_error_json(self, status: int, message: str):
        self.send_json(status, {'error': message})

    def read_json(self) -> dict:
        if hasattr(self, '_parsed_json'):
            return self._parsed_json
        raw_len = int(self.headers.get('Content-Length', '0'))
        if raw_len > 1_000_000: raise ApiError(413, 'Request body is too large.')
        try:
            raw = b''
            remaining = raw_len
            while remaining > 0:
                chunk = self.rfile.read(min(remaining, 65536))
                if not chunk:
                    break
                raw += chunk
                remaining -= len(chunk)
            self._body_read = True
            text = raw.decode('utf-8').strip() if raw else '{}'
            data = json.loads(text or '{}')
            if not isinstance(data, dict): raise ValueError()
            self._parsed_json = data
            return data
        except (ValueError, json.JSONDecodeError):
            raise ApiError(400, 'Request body must be a JSON object.')

    def drain_rfile(self):
        try:
            if not getattr(self, '_body_read', False):
                raw_len = int(self.headers.get('Content-Length', '0'))
                remaining = raw_len
                while remaining > 0:
                    chunk = self.rfile.read(min(remaining, 65536))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                self._body_read = True
        except Exception:
            pass

    def route_parts(self):
        parsed = urlparse(self.path)
        return parsed.path.rstrip('/') or '/', parse_qs(parsed.query)

    def get_session(self, required: bool = True):
        cookie = SimpleCookie(self.headers.get('Cookie', ''))
        morsel = cookie.get('ap_session')
        token = morsel.value if morsel else ''
        if not token:
            if required: raise ApiError(401, 'Sign in to continue.')
            return None
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        con = db()
        row = con.execute('SELECT s.*,u.id,u.name,u.email,u.role,u.status,u.domain_id FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=?', (token_hash,)).fetchone()
        if not row or row['expires_at'] <= stamp() or row['status'] != 'Active':
            if row:
                con.execute('DELETE FROM sessions WHERE token_hash=?', (token_hash,))
            if required: raise ApiError(401, 'Your session timed out due to inactivity. Sign in again.')
            return None
        # Slide session expiration window on activity
        new_expires = stamp(now_utc() + timedelta(minutes=SESSION_IDLE_MINUTES))
        con.execute('UPDATE sessions SET expires_at=? WHERE token_hash=?', (new_expires, token_hash))
        return row

    def require(self, role: str | None = None, mutation: bool = False):
        session = self.get_session()
        if role and session['role'] != role: raise ApiError(403, 'You do not have access to this action.')
        if mutation and not hmac.compare_digest(self.headers.get('X-CSRF-Token', ''), session['csrf_token']):
            raise ApiError(403, 'Session check failed. Refresh and try again.')
        return session

    def do_GET(self): self.dispatch('GET')
    def do_POST(self): self.dispatch('POST')
    def do_PATCH(self): self.dispatch('PATCH')
    def do_DELETE(self): self.dispatch('DELETE')
    def do_PUT(self): self.dispatch('PUT')

    def dispatch(self, method: str):
        path, query = self.route_parts()
        if not path.startswith('/api/'):
            return self.static_file(path)
        try:
            result = self.api(method, path, query)
            status, value, headers = result if len(result) == 3 else (*result, {})
            self.send_json(status, value, headers)
        except ApiError as err:
            self.send_error_json(err.status, err.message)
        except sqlite3.IntegrityError as err:
            self.send_error_json(409, 'That change conflicts with existing records.')
        except (ValueError, TypeError) as err:
            self.send_error_json(400, str(err) or 'Invalid request.')
        except Exception:
            self.log_error('Unhandled server error for %s', path)
            self.send_error_json(500, 'The server could not complete the request.')
        finally:
            self.drain_rfile()

    def api(self, method: str, path: str, query: dict):
        if path == '/api/health' and method == 'GET':
            return 200, {'ok': True, 'time': stamp()}
        if path == '/api/auth/login' and method == 'POST':
            data = self.read_json(); login = str(data.get('loginId', '')).strip(); password = str(data.get('password', ''))
            if len(login)>254 or len(password)>256: raise ApiError(401,'The ID or password is incorrect.')
            rate_key = self.client_address[0] + ':' + login.lower()
            attempts = [t for t in LOGIN_ATTEMPTS.get(rate_key, []) if time.monotonic()-t < 300]
            if len(attempts) >= 8: raise ApiError(429, 'Too many sign-in attempts. Wait five minutes and try again.')
            con = db(); user = con.execute('SELECT * FROM users WHERE (email=? OR id=?) AND status="Active"', (login, login)).fetchone()
            if not user or not password_matches(password, user['password_hash']):
                attempts.append(time.monotonic()); LOGIN_ATTEMPTS[rate_key] = attempts
                raise ApiError(401, 'The ID or password is incorrect.')
            LOGIN_ATTEMPTS.pop(rate_key, None)
            token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            initial_expires = stamp(now_utc() + timedelta(minutes=SESSION_IDLE_MINUTES))
            con.execute('INSERT INTO sessions VALUES(?,?,?, ?,?)', (hashlib.sha256(token.encode()).hexdigest(), user['id'], csrf, initial_expires, stamp()))
            secure = '; Secure' if COOKIE_SECURE else ''
            # Browser session cookie (expires when browser is closed, plus sliding 30-min idle timeout)
            cookie = f'ap_session={token}; HttpOnly; SameSite=Lax; Path=/{secure}'
            return 200, {'user': self.user_json(user), 'csrfToken': csrf}, {'Set-Cookie': cookie}
        if path == '/api/auth/logout' and method == 'POST':
            session = self.require(mutation=True)
            db().execute('DELETE FROM sessions WHERE token_hash=?', (hashlib.sha256(SimpleCookie(self.headers.get('Cookie',''))['ap_session'].value.encode()).hexdigest(),))
            return 200, {'ok': True}, {'Set-Cookie': 'ap_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0'}
        if path == '/api/auth/me' and method == 'GET':
            session = self.get_session(False)
            if not session: return 200, {'user': None}
            return 200, {'user': {'id':session['id'],'name':session['name'],'email':session['email'],'role':session['role'],'domainId':session['domain_id']},'csrfToken':session['csrf_token']}

        if path == '/api/admin/domains' or path.startswith('/api/admin/domains/'):
            self.require('admin', method != 'GET')
            con = db()
            if method == 'GET':
                rows = con.execute('''SELECT d.*, (SELECT count(*) FROM users u WHERE u.domain_id=d.id AND u.role="student") students,
                    (SELECT count(*) FROM questions q WHERE q.domain_id=d.id) questions FROM domains d ORDER BY d.name''').fetchall()
                return 200, {'domains':[dict(r) for r in rows]}
            data = self.read_json()
            if method == 'POST':
                name = required_text(data,'name',100); category=enum(data.get('category'),['Software','Electrical / Electronics'],'category')
                desc=clean_text(data.get('description',''),500); icon=clean_text(data.get('icon','◈'),8)
                cur=con.execute('INSERT INTO domains(name,category,description,icon,created_at) VALUES(?,?,?,?,?)', (name,category,desc,icon,stamp()))
                dom=dict(con.execute('SELECT * FROM domains WHERE id=?',(cur.lastrowid,)).fetchone())
                sync_sheets_row('Domains', {'ID': dom['id'], 'Name': dom['name'], 'Category': dom['category'], 'Description': dom['description'], 'Icon': dom['icon'], 'Status': dom['status'], 'Created At': dom['created_at']})
                return 201, {'domain': dom}
            did = int(path_id(path)); row=con.execute('SELECT * FROM domains WHERE id=?',(did,)).fetchone()
            if not row: raise ApiError(404,'Domain not found.')
            if method == 'PATCH':
                fields={'name':required_text(data,'name',100),'category':enum(data.get('category',row['category']),['Software','Electrical / Electronics'],'category'),'description':clean_text(data.get('description',row['description']),500),'icon':clean_text(data.get('icon',row['icon']),8),'status':enum(data.get('status',row['status']),['Active','Archived'],'status')}
                con.execute('UPDATE domains SET name=?,category=?,description=?,icon=?,status=? WHERE id=?',(*fields.values(),did))
                dom=dict(con.execute('SELECT * FROM domains WHERE id=?',(did,)).fetchone())
                sync_sheets_row('Domains', {'ID': dom['id'], 'Name': dom['name'], 'Category': dom['category'], 'Description': dom['description'], 'Icon': dom['icon'], 'Status': dom['status'], 'Created At': dom['created_at']})
                return 200, {'domain': dom}
            if method == 'DELETE':
                linked=con.execute('SELECT (SELECT count(*) FROM users WHERE domain_id=?)+(SELECT count(*) FROM questions WHERE domain_id=?)+(SELECT count(*) FROM assessments WHERE domain_id=?) n',(did,did,did)).fetchone()['n']
                if linked: raise ApiError(409,'Domain has linked students, questions, or assessments. Archive it instead.')
                con.execute('DELETE FROM domains WHERE id=?',(did,)); return 200, {'ok':True}

        if path == '/api/admin/sheets/config':
            self.require('admin', method != 'GET')
            if method == 'GET':
                url = get_sheets_url()
                return 200, {'webhookUrl': url, 'configured': bool(url)}
            if method == 'POST':
                data = self.read_json()
                url = str(data.get('webhookUrl', '')).strip()
                if url and not (url.startswith('https://script.google.com/') or url.startswith('http://') or url.startswith('https://')):
                    raise ApiError(400, 'Invalid Google Sheets Webhook URL. It must start with https://script.google.com/')
                set_setting('sheets_webhook_url', url)
                return 200, {'ok': True, 'webhookUrl': url, 'configured': bool(url)}

        if path == '/api/admin/sheets/sync_all' and method == 'POST':
            self.require('admin', True)
            self.read_json()
            res = sync_sheets_all()
            return 200, res

        if path == '/api/admin/sheets/pull_all' and method == 'POST':
            self.require('admin', True)
            self.read_json()
            res = pull_sheets_all()
            return 200, res

        if path == '/api/admin/settings/retention':
            self.require('admin', method != 'GET')
            if method == 'GET':
                return 200, {'retentionDays': get_retention_days(), 'default': RETENTION_DAYS_DEFAULT}
            if method == 'POST':
                data = self.read_json()
                days = data.get('retentionDays')
                try:
                    days = int(days)
                    if not 1 <= days <= 3650:
                        raise ValueError()
                except (TypeError, ValueError):
                    raise ApiError(400, 'Retention period must be between 1 and 3650 days.')
                set_setting('retention_days', str(days))
                return 200, {'ok': True, 'retentionDays': days}

        if path == '/api/admin/cleanup' and method == 'POST':
            self.require('admin', True)
            self.read_json()
            result = cleanup_old_data()
            return 200, {'ok': True, 'deleted': result}

        if path == '/api/admin/students/bulk' and method == 'POST':
            self.require('admin', True); con = db(); data = self.read_json()
            items = data.get('students')
            if not isinstance(items, list) or not 1 <= len(items) <= 500:
                raise ApiError(400, 'Bulk student import must contain between 1 and 500 students.')
            con.execute('BEGIN IMMEDIATE'); inserted = []
            try:
                for item in items:
                    if not isinstance(item, dict): raise ApiError(400, 'Each student must be an object.')
                    sid = required_text(item, 'id', 48); email = required_text(item, 'email', 254); name = required_text(item, 'name', 120); pwd = str(item.get('password', '')).strip()
                    if not pwd: pwd = f"{sid.lower()}@2026"
                    if not ID_RE.fullmatch(sid): raise ApiError(400, f'Student ID {sid} contains invalid characters.')
                    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email): raise ApiError(400, f'Invalid email: {email}')
                    dval = item.get('domainId') if item.get('domainId') is not None else item.get('domain')
                    dom = con.execute('SELECT id, name FROM domains WHERE name=? OR id=?', (str(dval or ''), int(dval) if str(dval or '').isdigit() else -1)).fetchone()
                    if not dom: raise ApiError(400, f'Domain not found for student {sid}.')
                    ph = password_hash(pwd if len(pwd) >= 6 else f"{sid.lower()}@2026")
                    con.execute('INSERT INTO users(id,role,name,email,password_hash,domain_id,created_at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,email=excluded.email,domain_id=excluded.domain_id', (sid, 'student', name, email, ph, dom['id'], stamp()))
                    sync_sheets_row('Students', {'Student ID': sid, 'Name': name, 'Email': email, 'Domain': dom['name'], 'Status': 'Active', 'Created At': stamp()})
                    inserted.append(sid)
                con.execute('COMMIT')
            except Exception:
                con.execute('ROLLBACK'); raise
            return 201, {'ids': inserted, 'count': len(inserted)}

        if path == '/api/admin/students' or path.startswith('/api/admin/students/'):
            self.require('admin', method != 'GET'); con=db()
            if method == 'GET':
                rows=con.execute('SELECT u.id,u.name,u.email,u.status,u.domain_id,d.name domain FROM users u LEFT JOIN domains d ON d.id=u.domain_id WHERE u.role="student" ORDER BY u.name').fetchall()
                return 200, {'students':[dict(r) for r in rows]}
            data=self.read_json()
            if method == 'POST':
                sid=required_text(data,'id',48); email=required_text(data,'email',254); name=required_text(data,'name',120); raw_pwd=str(data.get('password','')).strip()
                if not ID_RE.fullmatch(sid): raise ApiError(400,'Student ID can contain letters, numbers, hyphens, dots, and underscores only.')
                if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email): raise ApiError(400,'Enter a valid student email address.')
                if con.execute('SELECT 1 FROM users WHERE id=?',(sid,)).fetchone():
                    raise ApiError(409, f'A user or student with ID "{sid}" already exists.')
                if con.execute('SELECT 1 FROM users WHERE email=? COLLATE NOCASE',(email,)).fetchone():
                    raise ApiError(409, f'A student with email "{email}" already exists.')
                domain_val = data.get('domainId') if data.get('domainId') is not None else data.get('domain')
                domain=con.execute('SELECT id,name FROM domains WHERE name=? OR id=?',(str(domain_val or ''),int(domain_val) if str(domain_val or '').isdigit() else -1)).fetchone()
                if not domain:
                    active_doms = con.execute('SELECT id,name FROM domains WHERE status="Active" ORDER BY id').fetchall()
                    if len(active_doms) == 1 and not domain_val:
                        domain = active_doms[0]
                    else:
                        raise ApiError(400,'Select a valid domain.')
                if raw_pwd:
                    if len(raw_pwd) < 6: raise ApiError(400, 'Password must be at least 6 characters.')
                    effective_pwd = raw_pwd
                    temp_pwd = None
                else:
                    effective_pwd = f"{sid.lower()}@2026"
                    temp_pwd = effective_pwd
                ph=password_hash(effective_pwd)
                con.execute('INSERT INTO users(id,role,name,email,password_hash,domain_id,created_at) VALUES(?,?,?,?,?,?,?)',(sid,'student',name,email,ph,domain['id'],stamp()))
                sync_sheets_row('Students', {'Student ID': sid, 'Name': name, 'Email': email, 'Domain': domain['name'], 'Status': 'Active', 'Created At': stamp()})
                return 201, {'student':{'id':sid,'name':name,'email':email,'domainId':domain['id'],'domain':domain['name'],'status':'Active'}, 'temporaryPassword': temp_pwd}
            sid=unquote(path.rsplit('/',1)[-1]); row=con.execute('SELECT * FROM users WHERE id=? AND role="student"',(sid,)).fetchone()
            if not row: raise ApiError(404,'Student not found.')
            data=self.read_json()
            if method=='PATCH':
                name=required_text(data,'name',120); email=required_text(data,'email',254); status=enum(data.get('status','Active'),['Active','Disabled'],'status')
                if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email): raise ApiError(400,'Enter a valid student email address.')
                dval = data.get('domainId') if data.get('domainId') is not None else data.get('domain', row['domain_id'])
                domain=con.execute('SELECT id,name FROM domains WHERE name=? OR id=?',(str(dval or ''), int(dval) if str(dval or '').isdigit() else -1)).fetchone()
                if not domain: raise ApiError(400,'Select a valid domain.')
                con.execute('UPDATE users SET name=?,email=?,domain_id=?,status=? WHERE id=?',(name,email,domain['id'],status,sid))
                if data.get('password'):
                    pwd = str(data['password']).strip()
                    if len(pwd) < 6: raise ApiError(400, 'Password must be at least 6 characters.')
                    con.execute('UPDATE users SET password_hash=? WHERE id=?',(password_hash(pwd),sid))
                sync_sheets_row('Students', {'Student ID': sid, 'Name': name, 'Email': email, 'Domain': domain['name'], 'Status': status, 'Created At': stamp()})
                return 200, {'ok':True}

        if path == '/api/admin/questions' or path.startswith('/api/admin/questions/'):
            self.require('admin', method != 'GET'); con=db()
            if method == 'GET':
                domain_id=query.get('domainId',[None])[0]; typ=query.get('type',[None])[0]
                sql='SELECT * FROM questions'; clauses=[]; args=[]
                if domain_id: clauses.append('domain_id=?'); args.append(int(domain_id))
                if typ: clauses.append('type=?'); args.append(enum(typ,['MCQ','Coding'],'type'))
                if clauses: sql+=' WHERE '+' AND '.join(clauses)
                rows=con.execute(sql+' ORDER BY created_at DESC',args).fetchall()
                return 200, {'questions':[safe_question(r) | {'data':json.loads(r['data_json'])} for r in rows]}
            data=self.read_json()
            if path == '/api/admin/questions/bulk' and method=='POST':
                items=data.get('questions')
                if not isinstance(items,list) or not 1<=len(items)<=500: raise ApiError(400,'Bulk import must contain between 1 and 500 questions.')
                con.execute('BEGIN IMMEDIATE'); inserted=[]
                try:
                    for item in items:
                        if not isinstance(item,dict): raise ApiError(400,'Each imported question must be an object.')
                        q=validate_question(item); did=domain_id_for(con,item.get('domainId')); qid='Q-'+secrets.token_hex(6)
                        con.execute('INSERT INTO questions(id,domain_id,type,title,difficulty,data_json,status,created_at) VALUES(?,?,?,?,?,?,?,?)',(qid,did,q['type'],q['title'],q['difficulty'],json.dumps(q['data'],ensure_ascii=False),q['status'],stamp()))
                        dom=con.execute('SELECT name FROM domains WHERE id=?',(did,)).fetchone()
                        _opts = ' | '.join(q['data'].get('options', [])) if q['type'] == 'MCQ' else ''
                        _correct = q['data'].get('correctOption', '') if q['type'] == 'MCQ' else ''
                        _langs = ', '.join(q['data'].get('languages', [])) if q['type'] == 'Coding' else ''
                        _sample = len(q['data'].get('sampleTests', [])) if q['type'] == 'Coding' else ''
                        _hidden = len(q['data'].get('hiddenTests', [])) if q['type'] == 'Coding' else ''
                        _tlimit = q['data'].get('timeLimitSeconds', '') if q['type'] == 'Coding' else ''
                        _mlimit = q['data'].get('memoryLimitMB', '') if q['type'] == 'Coding' else ''
                        sync_sheets_row('Questions', {'Question ID': qid, 'Domain': dom['name'] if dom else '', 'Type': q['type'], 'Difficulty': q['difficulty'], 'Title': q['title'], 'Options': _opts, 'Correct Option': _correct, 'Languages': _langs, 'Sample Tests': _sample, 'Hidden Tests': _hidden, 'Time Limit (s)': _tlimit, 'Memory Limit (MB)': _mlimit, 'Status': q['status'], 'Created At': stamp()})
                        inserted.append(qid)
                    con.execute('COMMIT')
                except Exception:
                    con.execute('ROLLBACK'); raise
                return 201, {'ids':inserted,'count':len(inserted)}
            if method in ('POST','PATCH'):
                q=validate_question(data); qid=unquote(path.rsplit('/',1)[-1]) if method=='PATCH' else 'Q-'+secrets.token_hex(6)
                did=domain_id_for(con,data.get('domainId'))
                if method=='PATCH':
                    old=con.execute('SELECT version FROM questions WHERE id=?',(qid,)).fetchone()
                    if not old: raise ApiError(404,'Question not found.')
                    con.execute('UPDATE questions SET domain_id=?,type=?,title=?,difficulty=?,data_json=?,status=?,version=version+1 WHERE id=?',(did,q['type'],q['title'],q['difficulty'],json.dumps(q['data'],ensure_ascii=False),q['status'],qid))
                else:
                    con.execute('INSERT INTO questions(id,domain_id,type,title,difficulty,data_json,status,created_at) VALUES(?,?,?,?,?,?,?,?)',(qid,did,q['type'],q['title'],q['difficulty'],json.dumps(q['data'],ensure_ascii=False),q['status'],stamp()))
                dom=con.execute('SELECT name FROM domains WHERE id=?',(did,)).fetchone()
                _opts = ' | '.join(q['data'].get('options', [])) if q['type'] == 'MCQ' else ''
                _correct = q['data'].get('correctOption', '') if q['type'] == 'MCQ' else ''
                _langs = ', '.join(q['data'].get('languages', [])) if q['type'] == 'Coding' else ''
                _sample = len(q['data'].get('sampleTests', [])) if q['type'] == 'Coding' else ''
                _hidden = len(q['data'].get('hiddenTests', [])) if q['type'] == 'Coding' else ''
                _tlimit = q['data'].get('timeLimitSeconds', '') if q['type'] == 'Coding' else ''
                _mlimit = q['data'].get('memoryLimitMB', '') if q['type'] == 'Coding' else ''
                sync_sheets_row('Questions', {'Question ID': qid, 'Domain': dom['name'] if dom else '', 'Type': q['type'], 'Difficulty': q['difficulty'], 'Title': q['title'], 'Options': _opts, 'Correct Option': _correct, 'Languages': _langs, 'Sample Tests': _sample, 'Hidden Tests': _hidden, 'Time Limit (s)': _tlimit, 'Memory Limit (MB)': _mlimit, 'Status': q['status'], 'Created At': stamp()})
                return (201 if method=='POST' else 200), {'id':qid}
            if method=='DELETE':
                qid=unquote(path.rsplit('/',1)[-1]); cur=con.execute('UPDATE questions SET status="Archived",version=version+1 WHERE id=?',(qid,))
                if not cur.rowcount: raise ApiError(404,'Question not found.')
                return 200, {'ok':True}

        if path == '/api/admin/assessments' or path.startswith('/api/admin/assessments/'):
            self.require('admin', method != 'GET'); con=db()
            if method=='GET':
                rows=con.execute('''SELECT a.*,d.name domain,(SELECT count(*) FROM users u WHERE u.role="student" AND u.domain_id=a.domain_id AND u.status="Active") assigned FROM assessments a JOIN domains d ON d.id=a.domain_id ORDER BY a.starts_at''').fetchall()
                return 200, {'assessments':[dict(r) for r in rows]}
            data=self.read_json()
            if method in ('POST','PATCH'):
                title=required_text(data,'title',160); did=domain_id_for(con,data.get('domainId')); starts=parse_instant(data.get('startsAt'))
                aid=unquote(path.rsplit('/',1)[-1]) if method=='PATCH' else 'A-'+secrets.token_hex(5)
                old=con.execute('SELECT * FROM assessments WHERE id=?',(aid,)).fetchone() if method=='PATCH' else None
                if method=='PATCH' and not old: raise ApiError(404,'Assessment not found.')
                if method=='POST' and starts<=now_utc(): raise ApiError(400,'Assessment start time must be in the future.')
                if method=='PATCH' and starts<=now_utc() and stamp(starts)!=old['starts_at']: raise ApiError(400,'Assessment start time must be in the future.')
                duration=int(data.get('durationMinutes',45)); mcq=int(data.get('mcqCount',0)); coding=int(data.get('codingCount',0))
                if not 5<=duration<=240: raise ApiError(400,'Duration must be between 5 and 240 minutes.')
                if min(mcq,coding)<0 or mcq+coding<1: raise ApiError(400,'Choose at least one question; counts cannot be negative.')
                counts={r['type']:r['n'] for r in con.execute('SELECT type,count(*) n FROM questions WHERE domain_id=? AND status="Published" GROUP BY type',(did,))}
                if mcq>counts.get('MCQ',0): raise ApiError(400,f"This domain has {counts.get('MCQ',0)} published MCQs.")
                if coding>counts.get('Coding',0): raise ApiError(400,f"This domain has {counts.get('Coding',0)} published coding questions.")
                con.execute('''INSERT INTO assessments(id,domain_id,title,starts_at,duration_min,mcq_count,coding_count,status,created_at)
                  VALUES(?,?,?,?,?,?,?,? ,?) ON CONFLICT(id) DO UPDATE SET domain_id=excluded.domain_id,title=excluded.title,starts_at=excluded.starts_at,duration_min=excluded.duration_min,mcq_count=excluded.mcq_count,coding_count=excluded.coding_count,status=excluded.status''',
                  (aid,did,title,stamp(starts),duration,mcq,coding,enum(data.get('status','Scheduled'),['Scheduled','Draft','Cancelled'],'status'),stamp()))
                dom=con.execute('SELECT name FROM domains WHERE id=?',(did,)).fetchone()
                sync_sheets_row('Assessments', {'Assessment ID': aid, 'Title': title, 'Domain': dom['name'] if dom else '', 'Starts At (IST)': stamp(starts), 'Duration (min)': duration, 'MCQ Count': mcq, 'Coding Count': coding, 'Status': data.get('status','Scheduled')})
                return (201 if method=='POST' else 200), {'id':aid}

        if path == '/api/admin/flags' and method == 'GET':
            self.require('admin'); con=db()
            rows=con.execute('''SELECT e.id,e.event_type,e.detail,e.created_at,e.reviewed_at,u.name student,u.id student_id,a.title assessment
                FROM review_events e JOIN attempts t ON t.id=e.attempt_id JOIN users u ON u.id=t.student_id
                JOIN assessments a ON a.id=t.assessment_id ORDER BY e.created_at DESC LIMIT 500''').fetchall()
            return 200, {'flags':[dict(r) for r in rows]}
        if (path == '/api/admin/results' or path.startswith('/api/admin/results/')) and method == 'GET':
            self.require('admin'); con=db()
            if path != '/api/admin/results':
                attempt_id=unquote(path.rsplit('/',1)[-1])
                attempt=con.execute('''SELECT t.*,u.name student,u.id student_id,a.title assessment,d.name domain FROM attempts t
                    JOIN users u ON u.id=t.student_id JOIN assessments a ON a.id=t.assessment_id JOIN domains d ON d.id=a.domain_id WHERE t.id=?''',(attempt_id,)).fetchone()
                if not attempt: raise ApiError(404,'Attempt result not found.')
                questions=con.execute('''SELECT aq.question_id,aq.ordinal,aq.snapshot_json,aq.grading_json,an.answer_json FROM attempt_questions aq
                    LEFT JOIN answers an ON an.attempt_id=aq.attempt_id AND an.question_id=aq.question_id WHERE aq.attempt_id=? ORDER BY aq.ordinal''',(attempt_id,)).fetchall()
                answers=[]
                for q in questions:
                    question=json.loads(q['snapshot_json']); grading=json.loads(q['grading_json']); answer=json.loads(q['answer_json']) if q['answer_json'] else None
                    if question['type']=='MCQ':
                        selected=answer.get('optionIndex') if isinstance(answer,dict) else None; correct=ord(grading.get('correctOption','?'))-65 if grading.get('correctOption') in 'ABCD' else None
                        question['correctOption']=grading.get('correctOption'); question['selectedOption']=selected; question['isCorrect']=selected==correct
                    answers.append({'question':question,'answer':answer})
                return 200, {'attempt':dict(attempt),'answers':answers}
            rows=con.execute('''SELECT t.id,t.status,t.started_at,t.submitted_at,t.submit_reason,t.score,t.max_score,t.grading_status,
                u.id student_id,u.name student,a.id assessment_id,a.title assessment,d.name domain
                FROM attempts t JOIN users u ON u.id=t.student_id JOIN assessments a ON a.id=t.assessment_id
                JOIN domains d ON d.id=a.domain_id ORDER BY coalesce(t.submitted_at,t.started_at) DESC''').fetchall()
            return 200, {'results':[dict(r) for r in rows]}
        if path.startswith('/api/admin/flags/') and method=='PATCH':
            session=self.require('admin',True); fid=int(path.rsplit('/',1)[-1]); cur=db().execute('UPDATE review_events SET reviewed_at=?,reviewed_by=? WHERE id=? AND reviewed_at IS NULL',(stamp(),session['id'],fid))
            if not cur.rowcount: raise ApiError(404,'Open review flag not found.')
            return 200, {'ok':True}

        if path == '/api/student/home' and method=='GET':
            s=self.require('student'); con=db(); domain=con.execute('SELECT * FROM domains WHERE id=?',(s['domain_id'],)).fetchone()
            if not domain: raise ApiError(403,'No active domain is assigned to this account.')
            rows=con.execute('SELECT * FROM assessments WHERE domain_id=? AND status="Scheduled" ORDER BY starts_at',(domain['id'],)).fetchall()
            if domain['status']!='Active': rows=[]
            attempts=con.execute('SELECT id,assessment_id,status,submitted_at,deadline_at FROM attempts WHERE student_id=?',(s['id'],)).fetchall()
            attempted={r['assessment_id']:dict(r) for r in attempts}
            return 200, {'domain':dict(domain),'assessments':[dict(r)|{'attempt':attempted.get(r['id'])} for r in rows]}

        if path == '/api/student/attempts/start' and method=='POST':
            session=self.require('student',True); data=self.read_json(); aid=str(data.get('assessmentId','')); con=db()
            assessment=con.execute('SELECT a.*,d.status domain_status FROM assessments a JOIN domains d ON d.id=a.domain_id WHERE a.id=? AND a.domain_id=? AND a.status="Scheduled"',(aid,session['domain_id'])).fetchone()
            if not assessment or assessment['domain_status']!='Active': raise ApiError(404,'Assessment not found for your assigned domain.')
            start=parse_instant(assessment['starts_at']); end=start+timedelta(minutes=assessment['duration_min']); now=now_utc()
            if now<start: raise ApiError(425,'This assessment has not opened yet.')
            if now>=end: raise ApiError(410,'The scheduled assessment window has ended.')
            if con.execute('SELECT 1 FROM attempts WHERE assessment_id=? AND student_id=?',(aid,session['id'])).fetchone(): raise ApiError(409,'This assessment attempt has already been used.')
            attempt='T-'+secrets.token_hex(8)
            try:
                con.execute('BEGIN IMMEDIATE')
                con.execute('INSERT INTO attempts(id,assessment_id,student_id,started_at,deadline_at) VALUES(?,?,?,?,?)',(attempt,aid,session['id'],stamp(now),stamp(end)))
                selected=[]
                for typ,count in [('MCQ',assessment['mcq_count']),('Coding',assessment['coding_count'])]:
                    selected.extend(con.execute('SELECT * FROM questions WHERE domain_id=? AND type=? AND status="Published" ORDER BY random() LIMIT ?',(assessment['domain_id'],typ,count)).fetchall())
                if len(selected)!=assessment['mcq_count']+assessment['coding_count']:
                    con.execute('ROLLBACK'); raise ApiError(409,'The question pool changed. Contact your administrator before starting.')
                for idx,row in enumerate(selected):
                    con.execute('INSERT INTO attempt_questions VALUES(?,?,?,?,?)',(attempt,row['id'],idx,json.dumps(safe_question(row),ensure_ascii=False),row['data_json']))
                con.execute('COMMIT')
            except sqlite3.IntegrityError:
                con.execute('ROLLBACK'); raise ApiError(409,'This assessment attempt has already been used.')
            return 201, self.attempt_json(con,attempt,session['id'])

        if path.startswith('/api/student/attempts/'):
            session=self.require('student',method!='GET'); parts=path.split('/'); attempt_id=unquote(parts[4]) if len(parts)>4 else ''
            con=db(); attempt=con.execute('SELECT * FROM attempts WHERE id=? AND student_id=?',(attempt_id,session['id'])).fetchone()
            if not attempt: raise ApiError(404,'Attempt not found.')
            if len(parts)==5 and method=='GET':
                if attempt['status']=='In progress' and now_utc()>=parse_instant(attempt['deadline_at']):
                    con.execute('UPDATE attempts SET status="Expired",submitted_at=?,submit_reason="Time expired" WHERE id=?',(stamp(),attempt_id))
                    self.grade_attempt(con,attempt_id)
                return 200,self.attempt_json(con,attempt_id,session['id'])
            if len(parts)==7 and parts[5]=='answers' and method=='PUT':
                qid=unquote(parts[6]); data=self.read_json()
                if attempt['status']!='In progress' or now_utc()>=parse_instant(attempt['deadline_at']): raise ApiError(410,'This attempt is closed.')
                snapshot=con.execute('SELECT snapshot_json FROM attempt_questions WHERE attempt_id=? AND question_id=?',(attempt_id,qid)).fetchone()
                if not snapshot: raise ApiError(404,'Question is not part of this attempt.')
                question=json.loads(snapshot['snapshot_json']); answer=data.get('answer')
                if question['type']=='MCQ':
                    idx=answer.get('optionIndex') if isinstance(answer,dict) else None
                    if not isinstance(idx,int) or idx<0 or idx>=len(question.get('options',[])): raise ApiError(400,'Choose one of the listed answer options.')
                else:
                    if not isinstance(answer,dict) or answer.get('language') not in question.get('languages',[]) or not isinstance(answer.get('drafts'),dict): raise ApiError(400,'Coding answer must include an allowed language and code drafts.')
                    if any(not isinstance(k,str) or k not in question['languages'] or not isinstance(v,str) or len(v)>100_000 for k,v in answer['drafts'].items()): raise ApiError(400,'Invalid coding answer draft.')
                con.execute('INSERT INTO answers VALUES(?,?,?,?) ON CONFLICT(attempt_id,question_id) DO UPDATE SET answer_json=excluded.answer_json,updated_at=excluded.updated_at',(attempt_id,qid,json.dumps(answer,ensure_ascii=False),stamp()))
                return 200, {'savedAt':stamp()}
            if len(parts)==6 and parts[5]=='run' and method=='POST':
                data=self.read_json(); qid=str(data.get('questionId','')); language=enum(data.get('language'),list(SUPPORTED_LANGUAGES),'language'); source=clean_text(data.get('code',''),100_000)
                if attempt['status']!='In progress' or now_utc()>=parse_instant(attempt['deadline_at']): raise ApiError(410,'This attempt is closed.')
                aq=con.execute('SELECT aq.grading_json FROM attempt_questions aq WHERE aq.attempt_id=? AND aq.question_id=?',(attempt_id,qid)).fetchone()
                if not aq: raise ApiError(404,'Coding question is not part of this attempt.')
                qdata=json.loads(aq['grading_json'])
                if language not in qdata['languages']: raise ApiError(400,'That language is not enabled for this question.')
                tests=qdata.get('sampleTests')
                if not tests: raise ApiError(400,'This question has no public sample tests to run.')
                con.execute('INSERT INTO answers VALUES(?,?,?,?) ON CONFLICT(attempt_id,question_id) DO UPDATE SET answer_json=excluded.answer_json,updated_at=excluded.updated_at',(attempt_id,qid,json.dumps({'language':language,'drafts':{language:source}}),stamp()))
                results=run_isolated(language,source,tests,qdata.get('timeLimitSeconds',3))
                passed=sum(1 for r in results if r['passed'])
                return 200, {'passed':passed,'total':len(results),'results':[{'passed':r['passed'],'output':r['output'],'error':r['error']} for r in results]}
            if len(parts)==6 and parts[5]=='events' and method=='POST':
                data=self.read_json(); kind=enum(data.get('type'),['visibility','fullscreen'],'event type')
                con.execute('BEGIN IMMEDIATE'); row=con.execute('SELECT * FROM attempts WHERE id=?',(attempt_id,)).fetchone()
                if row['status']!='In progress': con.execute('ROLLBACK'); raise ApiError(410,'This attempt is closed.')
                if kind=='visibility':
                    count=row['visibility_events']+1; con.execute('UPDATE attempts SET visibility_events=? WHERE id=?',(count,attempt_id))
                    con.execute('INSERT INTO review_events(attempt_id,event_type,detail,created_at) VALUES(?,?,?,?)',(attempt_id,'visibility',f'Page visibility change {count}',stamp()))
                    if count>=3: self.finish_attempt(con,attempt_id,'Third visibility event')
                else:
                    count=row['fullscreen_events']+1; con.execute('UPDATE attempts SET fullscreen_events=? WHERE id=?',(count,attempt_id))
                    con.execute('INSERT INTO review_events(attempt_id,event_type,detail,created_at) VALUES(?,?,?,?)',(attempt_id,'fullscreen',f'Full-screen exit {count}',stamp()))
                con.execute('COMMIT')
                if kind=='visibility' and count>=3: self.grade_attempt(con,attempt_id)
                return 200, {'visibilityEvents':count,'autoSubmitted':kind=='visibility' and count>=3}
            if len(parts)==6 and parts[5]=='submit' and method=='POST':
                data=self.read_json(); con.execute('BEGIN IMMEDIATE'); row=con.execute('SELECT status,deadline_at FROM attempts WHERE id=?',(attempt_id,)).fetchone()
                if row['status']!='In progress': con.execute('ROLLBACK'); raise ApiError(410,'This attempt is already closed.')
                reason=clean_text(data.get('reason','Student submitted'),80) if now_utc()<parse_instant(row['deadline_at']) else 'Time expired'
                self.finish_attempt(con,attempt_id,reason); con.execute('COMMIT'); score=self.grade_attempt(con,attempt_id); return 200, {'ok':True,'submittedAt':stamp(),'score':score}

        raise ApiError(404, 'API endpoint not found.')

    def finish_attempt(self, con, attempt_id, reason):
        con.execute('UPDATE attempts SET status="Submitted",submitted_at=?,submit_reason=? WHERE id=?',(stamp(),reason,attempt_id))

    def grade_attempt(self, con, attempt_id):
        rows=con.execute('''SELECT aq.question_id,aq.snapshot_json,aq.grading_json,an.answer_json
            FROM attempt_questions aq LEFT JOIN answers an ON an.attempt_id=aq.attempt_id AND an.question_id=aq.question_id
            WHERE aq.attempt_id=? ORDER BY aq.ordinal''',(attempt_id,)).fetchall()
        score=0; pending=False
        for row in rows:
            question=json.loads(row['snapshot_json']); grading=json.loads(row['grading_json']); answer=json.loads(row['answer_json']) if row['answer_json'] else None
            if not answer: continue
            if question['type']=='MCQ':
                correct=grading.get('correctOption'); expected=ord(correct)-65 if correct in ('A','B','C','D') else -1
                if isinstance(answer,dict) and answer.get('optionIndex')==expected: score+=1
            elif isinstance(answer,dict) and answer.get('language') in question.get('languages',[]):
                code=answer.get('drafts',{}).get(answer['language'],'')
                try:
                    result=run_isolated(answer['language'],code,grading.get('hiddenTests',[]),grading.get('timeLimitSeconds',3))
                    if result and all(x.get('passed') for x in result): score+=1
                except ApiError as err:
                    if err.status==503: pending=True
                    else: raise
        status='Pending runner' if pending else 'Graded'
        con.execute('UPDATE attempts SET score=?,max_score=?,grading_status=? WHERE id=?',(score,len(rows),status,attempt_id))
        att=con.execute('''SELECT t.*, u.id student_id, u.name student_name, a.title assessment_title, coalesce(d.name, "") domain_name
            FROM attempts t JOIN users u ON u.id=t.student_id JOIN assessments a ON a.id=t.assessment_id
            LEFT JOIN domains d ON d.id=a.domain_id WHERE t.id=?''', (attempt_id,)).fetchone()
        if att:
            sync_sheets_row('Results', {
                'Attempt ID': att['id'],
                'Student ID': att['student_id'],
                'Student Name': att['student_name'],
                'Assessment': att['assessment_title'],
                'Domain': att['domain_name'],
                'Score': score,
                'Max Score': len(rows),
                'Status': att['status'],
                'Started At': att['started_at'],
                'Submitted At': att['submitted_at'],
                'Submit Reason': att['submit_reason'] or ''
            })
        return {'score':score,'maxScore':len(rows),'gradingStatus':status}

    def attempt_json(self, con, attempt_id, student_id):
        a=con.execute('SELECT t.*,asmt.title assessment_title,asmt.duration_min FROM attempts t JOIN assessments asmt ON asmt.id=t.assessment_id WHERE t.id=? AND t.student_id=?',(attempt_id,student_id)).fetchone()
        qs=con.execute('SELECT aq.question_id,aq.ordinal,aq.snapshot_json,an.answer_json FROM attempt_questions aq LEFT JOIN answers an ON an.attempt_id=aq.attempt_id AND an.question_id=aq.question_id WHERE aq.attempt_id=? ORDER BY aq.ordinal',(attempt_id,)).fetchall()
        return {'attempt':dict(a),'questions':[json.loads(q['snapshot_json'])|{'ordinal':q['ordinal'],'answer':json.loads(q['answer_json']) if q['answer_json'] else None} for q in qs]}

    def user_json(self,user): return {'id':user['id'],'name':user['name'],'email':user['email'],'role':user['role'],'domainId':user['domain_id']}

    def static_file(self, path):
        try:
            clean_path = unquote(path.split('?')[0]).strip('/')
            STATIC_ASSETS = {'styles.css', 'app.js', 'favicon.ico'}
            filename = Path(clean_path).name
            if filename in STATIC_ASSETS:
                target = (ROOT / filename).resolve()
            elif clean_path in STATIC_ASSETS:
                target = (ROOT / clean_path).resolve()
            else:
                target = (ROOT / 'index.html').resolve()
            if ROOT not in target.parents and target != ROOT:
                return self.send_error_json(404, 'Not found.')
            if not target.is_file():
                return self.send_error_json(404, 'Not found.')
            raw = target.read_bytes()
            mime = mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
            csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; media-src 'self' blob:; connect-src 'self' https://script.google.com https://script.googleusercontent.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
            self.send_response(200)
            self.send_header('Content-Type', mime + '; charset=utf-8' if mime.startswith('text/') or 'javascript' in mime else mime)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Connection', 'close')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', csp)
            self.end_headers()
            self.wfile.write(raw)
            self.close_connection = True
        except (ConnectionResetError, BrokenPipeError):
            pass

def clean_text(value, limit):
    if not isinstance(value,str) or len(value)>limit: raise ApiError(400,f'Text must be no longer than {limit} characters.')
    return value.strip()

def required_text(data,key,limit):
    value=clean_text(data.get(key,''),limit)
    if not value: raise ApiError(400,f'{key} is required.')
    return value

def enum(value, choices, label):
    if value not in choices: raise ApiError(400,f'Invalid {label}.')
    return value

def path_id(path):
    try: return int(unquote(path.rsplit('/',1)[-1]))
    except ValueError: raise ApiError(400,'Invalid record ID.')

def domain_id_for(con, value):
    try: did=int(value)
    except (ValueError,TypeError): raise ApiError(400,'Select a valid domain.')
    if not con.execute('SELECT 1 FROM domains WHERE id=? AND status="Active"',(did,)).fetchone(): raise ApiError(400,'Select an active domain.')
    return did

def validate_question(data):
    typ=enum(data.get('type'),['MCQ','Coding'],'question type'); title=required_text(data,'title',5000); difficulty=enum(data.get('difficulty'),['Easy','Medium','Hard'],'difficulty'); status=enum(data.get('status','Published'),['Published','Archived'],'status')
    content=data.get('data') or {}
    if not isinstance(content,dict): raise ApiError(400,'Question data must be an object.')
    if typ=='MCQ':
        options=content.get('options')
        if not isinstance(options,list) or not 2<=len(options)<=4 or any(not isinstance(x,str) or not x.strip() or len(x)>500 for x in options): raise ApiError(400,'MCQ needs between two and four non-empty options.')
        correct=content.get('correctOption')
        if correct not in ['A','B','C','D'] or ord(correct)-65>=len(options): raise ApiError(400,'Choose a correct option that exists.')
        clean={'options':[x.strip() for x in options],'correctOption':correct}
    else:
        langs=content.get('languages')
        if not isinstance(langs,list) or not langs or len(set(langs))!=len(langs) or any(x not in SUPPORTED_LANGUAGES for x in langs): raise ApiError(400,'Select one or more supported coding languages.')
        starters=content.get('starterCodes',{})
        if not isinstance(starters,dict) or any(k not in langs or not isinstance(v,str) or len(v)>100_000 for k,v in starters.items()): raise ApiError(400,'Starter code must be keyed by selected languages.')
        sample=content.get('sampleTests',[]); hidden=content.get('hiddenTests')
        if not isinstance(sample,list) or len(sample)>50 or any(not valid_test(t) for t in sample): raise ApiError(400,'Sample tests must contain at most 50 input/output objects.')
        if not isinstance(hidden,list) or not hidden or len(hidden)>50 or any(not valid_test(t) for t in hidden): raise ApiError(400,'Add 1–50 valid hidden tests.')
        clean={'languages':langs,'starterCodes':starters,'sampleTests':sample,'hiddenTests':hidden,'timeLimitSeconds':bounded_int(content.get('timeLimitSeconds',3),1,30,'time limit'),'memoryLimitMB':bounded_int(content.get('memoryLimitMB',256),32,2048,'memory limit')}
    return {'type':typ,'title':title,'difficulty':difficulty,'status':status,'data':clean}

def valid_test(value): return isinstance(value,dict) and set(('input','output')).issubset(value) and all(isinstance(value[k],(str,int,float,bool)) for k in ('input','output')) and len(str(value['input']))<10000 and len(str(value['output']))<10000
def bounded_int(value,low,high,label):
    try: value=int(value)
    except (TypeError,ValueError): raise ApiError(400,f'Invalid {label}.')
    if not low<=value<=high: raise ApiError(400,f'{label} must be between {low} and {high}.')
    return value

def run_isolated(language, source, tests, seconds):
    image=os.environ.get('ASSESSMENT_RUNNER_IMAGE','assessment-runner:local')
    try:
        probe=subprocess.run(['docker','image','inspect',image],capture_output=True,timeout=3)
    except (FileNotFoundError,subprocess.TimeoutExpired):
        raise ApiError(503,'The isolated coding runner is unavailable. Configure Docker and build the runner image.')
    if probe.returncode: raise ApiError(503,'The isolated coding runner image is not installed. Follow the setup guide to build it.')
    filenames={'Python':'main.py','JavaScript':'main.js','Java':'Main.java','C++':'main.cpp','C':'main.c'}
    with tempfile.TemporaryDirectory(prefix='assessment-code-') as directory:
        Path(directory,filenames[language]).write_text(source,encoding='utf-8')
        Path(directory,'tests.json').write_text(json.dumps(tests[:50],ensure_ascii=False),encoding='utf-8')
        Path(directory,'runner.py').write_bytes((ROOT/'runner'/'runner.py').read_bytes())
        cmd=['docker','run','--rm','--network','none','--memory=192m','--cpus=0.5','--pids-limit=48','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--user=65534:65534','--tmpfs','/tmp:rw,nosuid,nodev,size=32m,mode=1777','--mount',f'type=bind,src={directory},dst=/work,readonly',image,language,str(min(seconds,20))]
        try:
            done=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=min(180,20+len(tests[:50])*min(seconds,20)+15))
            payload=json.loads(done.stdout[:1_000_000].decode(errors='replace'))
            if payload.get('compileError'): return [{'passed':False,'output':'','error':payload['compileError'][:4000]}]
            return payload.get('results',[])[:50]
        except subprocess.TimeoutExpired:
            return [{'passed':False,'output':'','error':'The isolated runner exceeded its overall time limit.'}]
        except (ValueError,json.JSONDecodeError):
            return [{'passed':False,'output':'','error':'The isolated runner returned an invalid response.'}]

def bootstrap():
    init_db()
    # Clean up expired sessions on startup
    con = db()
    con.execute('DELETE FROM sessions WHERE expires_at < ?', (stamp(),))
    con.commit()
    email=os.environ.get('ASSESSMENT_BOOTSTRAP_ADMIN','').strip(); password=os.environ.get('ASSESSMENT_BOOTSTRAP_PASSWORD',''); name=os.environ.get('ASSESSMENT_BOOTSTRAP_NAME','Assessment Admin')
    if email and password:
        if not con.execute('SELECT 1 FROM users WHERE role="admin" LIMIT 1').fetchone():
            con.execute('INSERT INTO users(id,role,name,email,password_hash,created_at) VALUES(?,?,?,?,?,?)',('ADM-'+secrets.token_hex(5),'admin',name,email,password_hash(password),stamp()))
            print(f'Initial admin account created for {email}.')
    if get_sheets_url():
        try:
            res = pull_sheets_all()
            print(f'Synchronized from Google Sheets: {res.get("restored")}')
        except Exception as e:
            print(f'Sheets auto-sync notice on startup: {e}')
    if os.environ.get('ASSESSMENT_SEED_SAMPLE','')=='1': seed_sample()
    # Start background cleanup thread (runs every 24h, purges old attempts & sessions)
    threading.Thread(target=_run_daily_cleanup, daemon=True, name='daily-cleanup').start()
    print(f'Auto-cleanup enabled: records older than {get_retention_days()} days are purged daily.')

def seed_sample():
    con=db()
    if con.execute('SELECT 1 FROM domains LIMIT 1').fetchone(): return
    did=con.execute('INSERT INTO domains(name,category,description,icon,created_at) VALUES(?,?,?,?,?)',('Java Full Stack','Software','Java fundamentals and problem solving','☕',stamp())).lastrowid
    q1={'options':['static','final','private','abstract'],'correctOption':'B'}
    con.execute('INSERT INTO questions VALUES(?,?,?,?,?,?,?,?,?)',('Q-SAMPLE-1',did,'MCQ','Which keyword prevents a class from being subclassed?','Easy',json.dumps(q1),'Published',1,stamp()))
    q2={'languages':['Python','Java'],'starterCodes':{'Python':'def solve(value):\n    return ""','Java':'class Solution { public String solve(String value) { return ""; } }'},'sampleTests':[],'hiddenTests':[{'input':'x','output':'x'}],'timeLimitSeconds':3,'memoryLimitMB':256}
    con.execute('INSERT INTO questions VALUES(?,?,?,?,?,?,?,?,?)',('Q-SAMPLE-2',did,'Coding','Return the input string unchanged.','Easy',json.dumps(q2),'Published',1,stamp()))
    pw=os.environ.get('ASSESSMENT_DEMO_PASSWORD','')
    if pw:
        con.execute('INSERT INTO users(id,role,name,email,password_hash,domain_id,created_at) VALUES(?,?,?,?,?,?,?)',('ST-DEMO','student','Demo Student','student@example.test',password_hash(pw),did,stamp()))

if __name__=='__main__':
    bootstrap()
    httpd=ThreadingHTTPServer((HOST,PORT),Handler)
    print(f'Assessment Portal listening at http://{HOST}:{PORT} (IST schedules, timezone-aware API).')
    print('Use HTTPS behind a trusted reverse proxy for real student assessments.')
    try: httpd.serve_forever()
    except KeyboardInterrupt: print('\nShutting down.')
    finally: httpd.server_close()
