#!/usr/bin/env python3
"""Common utilities for question generation and database insertion."""
import json
import secrets
import datetime
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "assessment.sqlite3"

def now_stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

def make_mcq(title, options, correct_opt, difficulty='Medium'):
    assert len(options) == 4, f"MCQ must have exactly 4 options: {title}"
    assert correct_opt in ('A', 'B', 'C', 'D'), f"Invalid correct option: {correct_opt}"
    assert difficulty in ('Easy', 'Medium', 'Hard'), f"Invalid difficulty: {difficulty}"
    return {
        'type': 'MCQ',
        'title': title.strip(),
        'difficulty': difficulty,
        'status': 'Published',
        'data': {
            'options': [str(o).strip() for o in options],
            'correctOption': correct_opt
        }
    }

def make_coding(title, languages, starter_codes, sample_tests, hidden_tests, difficulty='Medium', time_limit=3, mem_limit=256):
    assert len(sample_tests) == 3, f"Coding question must have 3 sample tests, got {len(sample_tests)}"
    assert len(hidden_tests) == 15, f"Coding question must have 15 hidden tests, got {len(hidden_tests)}"
    return {
        'type': 'Coding',
        'title': title.strip(),
        'difficulty': difficulty,
        'status': 'Published',
        'data': {
            'languages': languages,
            'starterCodes': starter_codes,
            'sampleTests': sample_tests,
            'hiddenTests': hidden_tests,
            'timeLimitSeconds': time_limit,
            'memoryLimitMB': mem_limit
        }
    }

def insert_domain_questions(domain_name, questions):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id FROM domains WHERE name = ? COLLATE NOCASE", (domain_name,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Domain not found: {domain_name}")
    domain_id = row[0]
    
    # Clean old non-seeded or duplicate questions for this domain if needed, or check existing
    # Let's count existing
    cur.execute("SELECT count(*) FROM questions WHERE domain_id = ?", (domain_id,))
    count = cur.fetchone()[0]
    
    # We will insert all generated questions
    stamp = now_stamp()
    inserted = 0
    for q in questions:
        # Check if question with exact title exists in this domain
        cur.execute("SELECT id FROM questions WHERE domain_id = ? AND title = ?", (domain_id, q['title']))
        if cur.fetchone():
            continue
        qid = f"Q-{secrets.token_hex(6)}"
        cur.execute("""
            INSERT INTO questions(id, domain_id, type, title, difficulty, data_json, status, version, created_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (qid, domain_id, q['type'], q['title'], q['difficulty'], json.dumps(q['data'], ensure_ascii=False), q['status'], stamp))
        inserted += 1
    
    con.commit()
    cur.execute("SELECT count(*) FROM questions WHERE domain_id = ?", (domain_id,))
    total = cur.fetchone()[0]
    con.close()
    print(f"Domain '{domain_name}' (ID: {domain_id}): Inserted {inserted} new questions. Total in pool: {total}")
    return total

