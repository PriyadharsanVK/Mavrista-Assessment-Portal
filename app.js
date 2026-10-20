(() => {
  'use strict';

  const app = document.querySelector('#app');
  const modal = document.querySelector('#modal');
  const toastNode = document.querySelector('#toast');

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[ch]));

  const supportedLanguages = ['Java', 'Python', 'JavaScript', 'C++', 'C'];

  const EYE_ICON_SVG = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
  const EYE_OFF_ICON_SVG = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;

  const state = {
    user: null,
    csrf: '',
    page: 'Dashboard',
    domains: [],
    students: [],
    questions: [],
    assessments: [],
    results: [],
    flags: [],
    sheetsConfig: null,
    retentionDays: 90,
    studentHome: null,
    attempt: null,
    preflightAssessment: null,
    resumeAttemptId: null,
    index: 0,
    camera: null,
    tabEvents: 0,
    fullEvents: 0,
    timer: null,
    saveTimer: null,
    search: {
      domains: '',
      questions: '',
      students: '',
      assessments: '',
      results: ''
    },
    filter: {
      domainCategory: 'All',
      questionDomain: 'All',
      questionType: 'All',
      questionDifficulty: 'All',
      questionStatus: 'All',
      studentDomain: 'All'
    },
    questionTab: 'MCQ'
  };

  function toast(message, isError = false) {
    if (!toastNode) return;
    if (modal && modal.open) {
      if (toastNode.parentElement !== modal) {
        modal.appendChild(toastNode);
      }
    } else {
      if (toastNode.parentElement !== document.body) {
        document.body.appendChild(toastNode);
      }
    }
    toastNode.textContent = message;
    toastNode.classList.toggle('error', isError);
    toastNode.classList.add('show');
    clearTimeout(toastNode._timer);
    toastNode._timer = setTimeout(() => {
      toastNode.classList.remove('show');
      toastNode.classList.remove('error');
    }, 4500);
  }

  function showModalError(message) {
    const notice = $('#modalNotice');
    if (notice) {
      notice.hidden = false;
      notice.innerHTML = `<span>⚠️</span><div><strong>Validation / Submission error:</strong><div>${esc(message)}</div></div>`;
      notice.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function clearModalError() {
    const notice = $('#modalNotice');
    if (notice) {
      notice.hidden = true;
      notice.innerHTML = '';
    }
  }

  async function api(path, options = {}) {
    const headers = {
      'Accept': 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(state.csrf ? { 'X-CSRF-Token': state.csrf } : {}),
      ...(options.headers || {})
    };

    let response;
    try {
      response = await fetch(path, { credentials: 'same-origin', ...options, headers });
    } catch (_) {
      throw new Error('Cannot reach the assessment server. Verify it is running on 127.0.0.1:8000.');
    }

    const data = await response.json().catch(() => ({ error: 'The server returned an invalid response.' }));

    if (!response.ok) {
      if (response.status === 401 && state.user) {
        state.user = null;
        state.csrf = '';
        loginView(data.error || 'Your session expired. Please sign in again.');
      }
      throw new Error(data.error || `Request failed (${response.status}).`);
    }

    return data;
  }

  const post = (path, body) => api(path, { method: 'POST', body: JSON.stringify(body) });
  const patch = (path, body) => api(path, { method: 'PATCH', body: JSON.stringify(body) });
  const del = path => api(path, { method: 'DELETE' });

  function fmt(value) {
    if (!value) return '—';
    try {
      return new Date(value).toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short',
        timeZone: 'Asia/Kolkata'
      }) + ' IST';
    } catch (_) {
      return value || '—';
    }
  }

  function pill(text, kind = 'gray') {
    return `<span class="pill ${kind}"><i class="pill-dot"></i>${esc(text)}</span>`;
  }

  function pageHead(group, title, desc, action = '') {
    return `
      <div class="page-heading">
        <div>
          <div class="eyebrow">${esc(group)}</div>
          <h1>${esc(title)}</h1>
          <p>${esc(desc)}</p>
        </div>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">${action}</div>
      </div>
    `;
  }

  function field(label, name, value = '', type = 'text', extra = '') {
    if (type === 'password') {
      return `
        <div class="field">
          <label>${esc(label)}</label>
          <div class="password-input-wrap">
            <input name="${name}" type="password" value="${esc(value)}" ${extra}>
            <button type="button" class="password-toggle-btn" aria-label="Show password (2s preview)" title="Show password for 2 seconds">
              ${EYE_ICON_SVG}
            </button>
          </div>
        </div>
      `;
    }
    return `
      <div class="field">
        <label>${esc(label)}</label>
        <input name="${name}" type="${type}" value="${esc(value)}" ${extra}>
      </div>
    `;
  }

  function shell(content) {
    const nav = [
      { name: 'Dashboard', icon: '◫' },
      { name: 'Domains', icon: '◈' },
      { name: 'Question bank', icon: '▤' },
      { name: 'Students', icon: '♙' },
      { name: 'Assessments', icon: '▣' },
      { name: 'Results', icon: '📊' },
      { name: 'Review flags', icon: '⚑' }
    ];

    const unreviewedCount = state.flags.filter(f => !f.reviewed_at).length;

    app.innerHTML = `
      <div class="app-shell">
        <aside class="sidebar">
          <div class="brand">
            <div class="brand-mark">A</div>
            <div>
              <div class="brand-name">Assessment Portal</div>
              <div class="brand-sub">Skills Evaluation</div>
            </div>
          </div>
          <div class="workspace-chip">
            <i class="workspace-dot"></i>
            <div>
              <strong>Company Workspace</strong>
              <small>Administrator View</small>
            </div>
          </div>
          <div class="nav-label">Workspace</div>
          <nav class="nav-list">
            ${nav.map(n => `
              <button type="button" class="nav-item ${state.page === n.name ? 'active' : ''}" data-page="${n.name}">
                <span class="nav-ico">${n.icon}</span>
                <span>${n.name}</span>
                ${n.name === 'Review flags' && unreviewedCount > 0 ? `<span class="nav-count">${unreviewedCount}</span>` : ''}
              </button>
            `).join('')}
          </nav>
          <div class="sidebar-spacer"></div>
          <div class="sidebar-note">
            <b>Google Sheets & Local SQLite</b>
            Connected & ready. Export reports or sync data anytime.
          </div>
            <div class="profile-mini">
            <div class="avatar">${esc((state.user?.name || 'A').slice(0, 2).toUpperCase())}</div>
            <div>
              <strong>${esc(state.user?.name || 'Admin')}</strong>
              <small>Administrator</small>
            </div>
            <button type="button" class="signout-btn" title="Sign out" data-action="signout">⏻ Sign Out</button>
          </div>
        </aside>
        <section class="main">
          <header class="topbar">
            <button type="button" class="icon-button mobile-menu" data-action="menu">☰</button>
            <div class="breadcrumbs">Workspace <span> / </span><b>${esc(state.page)}</b></div>
            <div class="top-actions">
              <button type="button" class="button secondary small" data-modal="sheets-sync" title="Google Sheets live webhook configuration">
                <span style="color:${state.sheetsConfig?.configured ? '#1b7f4f' : '#888'}">${state.sheetsConfig?.configured ? '●' : '○'}</span>
                ${state.sheetsConfig?.configured ? 'Sheets Connected' : 'Sheets Sync'}
              </button>
              <div class="timezone">◷ <span>IST · Asia/Kolkata</span></div>
              <div class="top-avatar">${esc((state.user?.name || 'A').slice(0, 2).toUpperCase())}</div>
            </div>
          </header>
          ${content}
        </section>
      </div>
    `;
  }

  // Inactivity auto-logout (30 minutes of idle time)
  const INACTIVITY_TIMEOUT_MS = 30 * 60 * 1000;
  let inactivityTimer = null;

  function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    if (!state.user || state.attempt) return; // Do not interrupt active timed assessment
    inactivityTimer = setTimeout(async () => {
      if (!state.user || state.attempt) return;
      try {
        await post('/api/auth/logout', {});
      } catch (_) {}
      clearCamera();
      clearInterval(state.timer);
      state.timer = null;
      state.user = null;
      state.csrf = '';
      state.attempt = null;
      loginView('You have been logged out due to 30 minutes of inactivity. Please sign in again.');
    }, INACTIVITY_TIMEOUT_MS);
  }

  ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'].forEach(evt => {
    window.addEventListener(evt, resetInactivityTimer, { passive: true });
  });

  function loginView(message = '') {
    clearTimeout(inactivityTimer);
    if (window.location.pathname !== '/login' && window.location.pathname !== '/admin/login') {
      history.replaceState({ page: '__login__' }, '', '/login');
    }
    app.innerHTML = `
      <section class="login-shell">
        <div class="login-wrap">
          <div class="login-art">
            <div class="brand">
              <div class="brand-mark">A</div>
              <div>
                <div class="brand-name">Assessment Portal</div>
                <div class="brand-sub">Skills Evaluation</div>
              </div>
            </div>
            <div>
              <h1>Assess skills with clarity.</h1>
              <p>A secure workspace for scheduled assessments, domain tracking, and trusted results.</p>
            </div>
            <div class="login-foot">Assessment workspace · India Standard Time (IST)</div>
          </div>
          <form class="login-form" id="loginForm">
            <div class="eyebrow">Welcome back</div>
            <h2>Sign in to continue</h2>
            <p>Use the admin email or student ID provided for your account.</p>
            ${message ? `<div class="notice" style="border-color:#f1c2bb;background:#fff2f0;color:#9b2a22;margin-bottom:15px;" role="alert">${esc(message)}</div>` : ''}
            <div class="field">
              <label for="loginId">Admin email or Student ID</label>
              <input id="loginId" name="loginId" autocomplete="username" placeholder="e.g. admin@company.com or ST-101" required>
            </div>
            <div class="field">
              <label for="password">Password</label>
              <div class="password-input-wrap">
                <input id="password" name="password" type="password" autocomplete="current-password" placeholder="••••••••••••" required>
                <button type="button" class="password-toggle-btn" aria-label="Show password (2s preview)" title="Show password for 2 seconds">
                  ${EYE_ICON_SVG}
                </button>
              </div>
            </div>
            <button class="button primary full" type="submit" style="margin-top:10px">Sign in <span>→</span></button>
            <div class="login-help">No public self-registration. Contact your portal administrator for credential access.</div>
          </form>
        </div>
      </section>
    `;
  }

  function renderLogin() {
    loginView();
  }

  async function refreshAdmin() {
    const [d, q, s, a, r, f, sc, ret] = await Promise.all([
      api('/api/admin/domains'),
      api('/api/admin/questions'),
      api('/api/admin/students'),
      api('/api/admin/assessments'),
      api('/api/admin/results'),
      api('/api/admin/flags'),
      api('/api/admin/sheets/config').catch(() => ({ configured: false, webhookUrl: '' })),
      api('/api/admin/settings/retention').catch(() => ({ retentionDays: 90 }))
    ]);
    state.domains = d.domains || [];
    state.questions = q.questions || [];
    state.students = s.students || [];
    state.assessments = a.assessments || [];
    state.results = r.results || [];
    state.flags = f.flags || [];
    state.sheetsConfig = sc;
    state.retentionDays = ret.retentionDays || 90;
    renderAdmin();
  }

  // SPA URL routing — maps browser URL paths ↔ admin page names
  const PAGE_ROUTES = {
    '/admin/dashboard': 'Dashboard',
    '/admin/domains': 'Domains',
    '/admin/questions': 'Question bank',
    '/admin/students': 'Students',
    '/admin/assessments': 'Assessments',
    '/admin/results': 'Results',
    '/admin/flags': 'Review flags',
    '/student/home': '__student__',
    '/student/exam': '__student__',
    '/login': '__login__',
    '/admin/login': '__login__'
  };
  const PAGE_PATHS = {
    'Dashboard': '/admin/dashboard',
    'Domains': '/admin/domains',
    'Question bank': '/admin/questions',
    'Students': '/admin/students',
    'Assessments': '/admin/assessments',
    'Results': '/admin/results',
    'Review flags': '/admin/flags'
  };

  async function goPage(page) {
    state.page = page;
    // Update URL without reloading
    const urlPath = PAGE_PATHS[page];
    if (urlPath && window.location.pathname !== urlPath) {
      history.pushState({ page }, '', urlPath);
    }
    try {
      await refreshAdmin();
    } catch (e) {
      toast(e.message);
    }
  }

  // Handle browser back / forward buttons
  window.addEventListener('popstate', async e => {
    const page = e.state?.page || PAGE_ROUTES[window.location.pathname] || 'Dashboard';
    if (page === '__login__' || window.location.pathname === '/login' || window.location.pathname === '/admin/login') {
      if (state.user) {
        await post('/api/auth/logout', {}).catch(() => {});
        clearCamera();
        clearInterval(state.timer);
        state.timer = null;
        state.user = null;
        state.csrf = '';
        state.attempt = null;
      }
      loginView();
      return;
    }
    if (page === '__student__') {
      try { await loadStudentHome(); } catch (_) {}
    } else if (state.user?.role === 'admin') {
      state.page = page;
      try { await refreshAdmin(); } catch (_) {}
    }
  });

  function adminDashboard() {
    const active = state.assessments.filter(x => x.status === 'Scheduled').length;
    const pendingFlags = state.flags.filter(f => !f.reviewed_at).length;

    return `
      <div class="page">
        ${pageHead(
          'Overview',
          `Welcome, ${state.user?.name || 'Administrator'}`,
          'Manage domains, questions, student access, assessment schedules, and Google Sheets data.',
          `<button type="button" class="button primary" data-modal="assessment">＋ Schedule assessment</button>`
        )}

        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-head">Domains</div>
            <div class="stat-value">${state.domains.length}</div>
            <div class="stat-foot">Configured subject domains</div>
          </div>
          <div class="stat-card">
            <div class="stat-head">Students</div>
            <div class="stat-value">${state.students.length}</div>
            <div class="stat-foot">Enrolled student accounts</div>
          </div>
          <div class="stat-card">
            <div class="stat-head">Scheduled assessments</div>
            <div class="stat-value">${active}</div>
            <div class="stat-foot">Fixed start in IST</div>
          </div>
          <div class="stat-card">
            <div class="stat-head">Integrity review flags</div>
            <div class="stat-value">${pendingFlags}</div>
            <div class="stat-foot">${pendingFlags ? 'Events needing review' : 'All clear'}</div>
          </div>
        </div>

        <div class="dashboard-grid">
          <div>
            <section class="card">
              <div class="card-header">
                <div>
                  <div class="card-title">Upcoming assessments</div>
                  <div class="card-subtitle">Scheduled times in India Standard Time</div>
                </div>
                <button type="button" class="button ghost small" data-page="Assessments">View all →</button>
              </div>
              <div class="assessment-list">
                ${state.assessments.slice(0, 5).map(a => `
                  <div class="assessment-row">
                    <div class="assessment-mark">▣</div>
                    <div class="assessment-row-main">
                      <strong>${esc(a.title)}</strong>
                      <span>${esc(a.domain)} · ${fmt(a.starts_at)}</span>
                      <span>${a.mcq_count} MCQ + ${a.coding_count} coding</span>
                    </div>
                    ${pill(a.status, a.status === 'Scheduled' ? 'green' : 'gray')}
                  </div>
                `).join('') || '<div class="empty-state">No assessments scheduled yet. Click "+ Schedule assessment" to begin.</div>'}
              </div>
            </section>
          </div>

          <div>
            <section class="card">
              <div class="card-title">Quick actions</div>
              <div class="quick-actions" style="margin-top:14px">
                <button type="button" class="quick-action" data-modal="domain">
                  <span class="qa-icon">◈</span>
                  <b>Add a domain</b>
                  <span>Create a subject area</span>
                </button>
                <button type="button" class="quick-action" data-modal="question">
                  <span class="qa-icon">＋</span>
                  <b>Add question</b>
                  <span>MCQ or coding problem</span>
                </button>
                <button type="button" class="quick-action" data-modal="student">
                  <span class="qa-icon">♙</span>
                  <b>Provision student</b>
                  <span>Assign one domain</span>
                </button>
                <button type="button" class="quick-action" data-modal="assessment">
                  <span class="qa-icon">▣</span>
                  <b>Schedule exam</b>
                  <span>Set time and pool counts</span>
                </button>
              </div>
            </section>

            <section class="card section-gap">
              <div class="card-title" style="margin-bottom:8px">Google Sheets & Data Tools</div>
              <p class="helper" style="margin-bottom:12px">Sync assessment results, student records, and questions with Google Sheets.</p>
              <div style="display:flex;gap:8px;flex-direction:column">
                <button type="button" class="button secondary small" data-action="export-results">↓ Export results to CSV / Sheets</button>
                <button type="button" class="button secondary small" data-modal="bulk">↑ Import questions (CSV / Sheets)</button>
                <button type="button" class="button secondary small" data-modal="bulk-student">↑ Bulk import students (CSV / Sheets)</button>
              </div>
            </section>
          </div>
        </div>
      </div>
    `;
  }

  function domainsPage() {
    const q = (state.search.domains || '').toLowerCase().trim();
    const cat = state.filter.domainCategory;

    const filtered = state.domains.filter(d => {
      const matchCat = cat === 'All' || d.category === cat;
      const matchQ = !q || d.name.toLowerCase().includes(q) || (d.description || '').toLowerCase().includes(q);
      return matchCat && matchQ;
    });

    return `
      <div class="page">
        ${pageHead(
          'Catalog',
          'Domains',
          'Organize question pools and student access by domain (Software or Electrical / Electronics).',
          `<button type="button" class="button primary" data-modal="domain">＋ Add domain</button>`
        )}

        <div class="toolbar">
          <div class="search">
            <input type="text" id="domainSearch" placeholder="Search domains by name or keyword..." value="${esc(state.search.domains)}">
          </div>
          <div class="filter-tabs">
            ${['All', 'Software', 'Electrical / Electronics'].map(c => `
              <button type="button" class="filter-tab ${cat === c ? 'active' : ''}" data-filter-domain-cat="${c}">${c}</button>
            `).join('')}
          </div>
        </div>

        <div class="domain-grid">
          ${filtered.map(d => `
            <article class="domain-card">
              <div class="domain-symbol">${esc(d.icon || '◈')}</div>
              <h3>${esc(d.name)}</h3>
              <p>${esc(d.category)} · ${esc(d.description || 'Domain assessment area')}</p>
              <div class="tag-row">
                <span class="tag">${d.questions ?? 0} questions</span>
                <span class="tag">${d.students ?? 0} students</span>
              </div>
              <div class="domain-meta">
                <span>Status: <b>${esc(d.status)}</b></span>
                <div style="margin-left:auto;display:flex;gap:8px">
                  <button type="button" class="link-button" data-edit-domain="${d.id}">Edit</button>
                  <button type="button" class="link-button" data-domain-status="${d.id}" data-status="${d.status === 'Active' ? 'Archived' : 'Active'}">${d.status === 'Active' ? 'Archive' : 'Restore'}</button>
                  <button type="button" class="link-button" style="color:var(--red)" data-domain-delete="${d.id}">Delete</button>
                </div>
              </div>
            </article>
          `).join('') || '<div class="empty-state" style="grid-column:1/-1">No domains match your filter. Click "+ Add domain" to create one.</div>'}
        </div>
      </div>
    `;
  }

  function questionsPage() {
    const q = (state.search.questions || '').toLowerCase().trim();
    const dFilter = state.filter.questionDomain || 'All';
    const diffFilter = state.filter.questionDifficulty || 'All';
    const statusFilter = state.filter.questionStatus || 'All';
    const currentTab = state.questionTab || 'MCQ';

    const mcqTotal = state.questions.filter(item => item.type === 'MCQ').length;
    const codingTotal = state.questions.filter(item => item.type === 'Coding').length;

    // Filter MCQ domains
    const activeDomains = state.domains.filter(d => {
      if (dFilter !== 'All' && String(d.id) !== dFilter) return false;
      if (d.name.toLowerCase() === 'general') {
        return state.questions.some(item => item.type === 'MCQ' && (item.domain_id === d.id || item.domainId === d.id));
      }
      return true;
    });

    const codingFiltered = state.questions.filter(item => {
      if (item.type !== 'Coding') return false;
      const matchDiff = diffFilter === 'All' || item.difficulty === diffFilter;
      const matchStat = statusFilter === 'All' || item.status === statusFilter;
      const matchQ = !q || item.title.toLowerCase().includes(q) || item.id.toLowerCase().includes(q);
      return matchDiff && matchStat && matchQ;
    });

    return `
      <div class="page">
        ${pageHead(
          'Question library',
          'Question bank',
          'Manage domain-specific MCQ questions and universal coding challenges.',
          `
            <button type="button" class="button secondary" data-action="export-questions">↓ Export CSV / Sheets</button>
            <button type="button" class="button secondary" data-modal="bulk">↑ Import CSV / Sheets</button>
            <button type="button" class="button primary" data-modal="question">＋ Add question</button>
          `
        )}

        <div class="filter-tabs" style="margin-bottom:18px">
          <button type="button" class="filter-tab ${currentTab === 'MCQ' ? 'active' : ''}" data-set-question-tab="MCQ">
            📝 Multiple Choice Questions (${mcqTotal})
          </button>
          <button type="button" class="filter-tab ${currentTab === 'Coding' ? 'active' : ''}" data-set-question-tab="Coding">
            💻 Coding Challenges (${codingTotal})
          </button>
        </div>

        <div class="toolbar">
          <div class="search">
            <input type="text" id="questionSearch" placeholder="${currentTab === 'MCQ' ? 'Search MCQ prompt or question ID...' : 'Search coding challenge or ID...'}" value="${esc(state.search.questions)}">
          </div>
          ${currentTab === 'MCQ' ? `
            <select class="select" id="questionDomainFilter">
              <option value="All">All Domains (${state.domains.length})</option>
              ${state.domains.map(d => `<option value="${d.id}" ${dFilter === String(d.id) ? 'selected' : ''}>${esc(d.name)}</option>`).join('')}
            </select>
          ` : ''}
          <select class="select" id="questionDifficultyFilter">
            <option value="All">All Difficulties</option>
            <option value="Easy" ${diffFilter === 'Easy' ? 'selected' : ''}>Easy</option>
            <option value="Medium" ${diffFilter === 'Medium' ? 'selected' : ''}>Medium</option>
            <option value="Hard" ${diffFilter === 'Hard' ? 'selected' : ''}>Hard</option>
          </select>
          <select class="select" id="questionStatusFilter">
            <option value="All">All Statuses</option>
            <option value="Published" ${statusFilter === 'Published' ? 'selected' : ''}>Published</option>
            <option value="Archived" ${statusFilter === 'Archived' ? 'selected' : ''}>Archived</option>
          </select>
        </div>

        ${currentTab === 'MCQ' ? `
          <div class="mcq-sections">
            ${activeDomains.map(d => {
              const domAllMcqs = state.questions.filter(item => item.type === 'MCQ' && (item.domain_id === d.id || item.domainId === d.id));
              const matching = domAllMcqs.filter(item => {
                const matchDiff = diffFilter === 'All' || item.difficulty === diffFilter;
                const matchStat = statusFilter === 'All' || item.status === statusFilter;
                const matchQ = !q || item.title.toLowerCase().includes(q) || item.id.toLowerCase().includes(q);
                return matchDiff && matchStat && matchQ;
              });

              if (q && matching.length === 0) return '';

              return `
                <section class="domain-group-card">
                  <div class="domain-group-head">
                    <div class="domain-group-title">
                      <span class="domain-symbol" style="width:30px;height:30px;font-size:13px">${d.symbol || '📘'}</span>
                      <h3>${esc(d.name)}</h3>
                      <span class="pill ${d.category === 'Electronics' ? 'amber' : 'gray'}">${esc(d.category || 'Software')}</span>
                      <span class="pill green">${matching.length} ${matching.length === 1 ? 'MCQ' : 'MCQs'}</span>
                    </div>
                    <div class="domain-group-actions">
                      <button type="button" class="button secondary small" data-add-domain-mcq="${d.id}">＋ Add MCQ to ${esc(d.name)}</button>
                    </div>
                  </div>
                  <div class="table-wrap">
                    <table class="data-table">
                      <thead>
                        <tr>
                          <th style="width:45%">Question</th>
                          <th>Options & Key</th>
                          <th>Difficulty</th>
                          <th>Status</th>
                          <th style="text-align:right">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        ${matching.map(item => `
                          <tr>
                            <td>
                              <div class="table-main">${esc(item.title)}</div>
                              <div class="table-meta"><code>${esc(item.id)}</code></div>
                            </td>
                            <td>
                              <div class="table-main">${(item.data?.options || []).length} Options</div>
                              <div class="table-meta">Correct Key: <strong>[${esc(item.data?.correctOption || 'A')}]</strong></div>
                            </td>
                            <td>${esc(item.difficulty)}</td>
                            <td>${pill(item.status, item.status === 'Published' ? 'green' : 'gray')}</td>
                            <td style="text-align:right">
                              <button type="button" class="link-button" data-edit-question="${esc(item.id)}">Edit</button>
                              <button type="button" class="link-button" data-archive-question="${esc(item.id)}">${item.status === 'Archived' ? 'Restore' : 'Archive'}</button>
                              <button type="button" class="link-button danger" data-delete-question="${esc(item.id)}" title="Permanently delete question">Delete</button>
                            </td>
                          </tr>
                        `).join('') || `
                          <tr>
                            <td colspan="5" style="text-align:center;padding:26px;color:var(--muted)">
                              No MCQ questions found in this domain.
                              <button type="button" class="link-button" data-add-domain-mcq="${d.id}">+ Add MCQ now</button>
                            </td>
                          </tr>
                        `}
                      </tbody>
                    </table>
                  </div>
                </section>
              `;
            }).join('') || '<div class="empty-state">No MCQ questions or domains match your search filter.</div>'}
          </div>
        ` : `
          <div class="coding-section">
            <div class="notice" style="margin-bottom:18px;background:#f3f7f5;border-color:#d4e5dc;">
              <strong>Universal Coding Problem Pool</strong>
              <p style="margin:4px 0 0">Coding challenges are drawn randomly from this universal pool for all software-track assessments (Java, Python, Cybersecurity, Full Stack, Data Science, etc.). The 8 electronics domains do not include coding questions.</p>
            </div>

            <section class="card">
              <div class="card-header">
                <div>
                  <h3 class="card-title">Coding Challenges (${codingFiltered.length})</h3>
                  <div class="card-subtitle">Shared universal pool for all non-electronics students</div>
                </div>
                <button type="button" class="button primary small" data-add-coding-question>＋ Add Coding Question</button>
              </div>

              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th style="width:38%">Problem Statement</th>
                      <th>Languages</th>
                      <th>Test Cases</th>
                      <th>Limits</th>
                      <th>Difficulty</th>
                      <th>Status</th>
                      <th style="text-align:right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${codingFiltered.map(item => {
                      const langs = (item.data?.languages || item.languages || ['Python']).join(', ');
                      const samples = item.data?.sampleTests || [];
                      const hiddens = item.data?.hiddenTests || [];
                      const timeL = item.data?.timeLimitSeconds || 3;
                      const memL = item.data?.memoryLimitMB || 256;
                      return `
                        <tr>
                          <td>
                            <div class="table-main">${esc(item.title)}</div>
                            <div class="table-meta"><code>${esc(item.id)}</code></div>
                          </td>
                          <td>${esc(langs)}</td>
                          <td>
                            <div class="table-main">${samples.length} public tests</div>
                            <div class="table-meta">${hiddens.length} hidden tests</div>
                          </td>
                          <td>${timeL}s · ${memL}MB</td>
                          <td>${esc(item.difficulty)}</td>
                          <td>${pill(item.status, item.status === 'Published' ? 'green' : 'gray')}</td>
                          <td style="text-align:right">
                            <button type="button" class="link-button" data-edit-question="${esc(item.id)}">Edit</button>
                            <button type="button" class="link-button" data-archive-question="${esc(item.id)}">${item.status === 'Archived' ? 'Restore' : 'Archive'}</button>
                            <button type="button" class="link-button danger" data-delete-question="${esc(item.id)}" title="Permanently delete question">Delete</button>
                          </td>
                        </tr>
                      `;
                    }).join('') || '<tr><td colspan="7" style="text-align:center;padding:34px;color:var(--muted)">No coding challenges found matching criteria. Click "+ Add Coding Question" or bulk import.</td></tr>'}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        `}
      </div>
    `;
  }

  function studentsPage() {
    const q = (state.search.students || '').toLowerCase().trim();
    const dFilter = state.filter.studentDomain;

    const filtered = state.students.filter(s => {
      const matchD = dFilter === 'All' || String(s.domain_id) === dFilter || String(s.domainId) === dFilter;
      const matchQ = !q || s.name.toLowerCase().includes(q) || s.email.toLowerCase().includes(q) || s.id.toLowerCase().includes(q);
      return matchD && matchQ;
    });

    return `
      <div class="page">
        ${pageHead(
          'Accounts',
          'Students',
          'Provision student accounts and assign them to exactly one domain.',
          `
            <button type="button" class="button secondary" data-action="export-students">↓ Export CSV / Sheets</button>
            <button type="button" class="button secondary" data-modal="bulk-student">↑ Bulk import students</button>
            <button type="button" class="button primary" data-modal="student">＋ Add student</button>
          `
        )}

        <div class="toolbar">
          <div class="search">
            <input type="text" id="studentSearch" placeholder="Search by name, student ID, or email..." value="${esc(state.search.students)}">
          </div>
          <select class="select" id="studentDomainFilter">
            <option value="All">All Domains</option>
            ${state.domains.map(d => `<option value="${d.id}" ${dFilter === String(d.id) ? 'selected' : ''}>${esc(d.name)}</option>`).join('')}
          </select>
        </div>

        <section class="card">
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>ID</th>
                  <th>Email</th>
                  <th>Domain</th>
                  <th>Status</th>
                  <th style="text-align:right">Actions</th>
                </tr>
              </thead>
              <tbody>
                ${filtered.map(s => `
                  <tr>
                    <td><strong>${esc(s.name)}</strong></td>
                    <td><code>${esc(s.id)}</code></td>
                    <td>${esc(s.email)}</td>
                    <td>${esc(s.domain || state.domains.find(d => d.id === s.domain_id)?.name || '—')}</td>
                    <td>${pill(s.status, s.status === 'Active' ? 'green' : 'gray')}</td>
                    <td style="text-align:right">
                      <button type="button" class="link-button" data-edit-student="${esc(s.id)}">Edit / Reset password</button>
                      <button type="button" class="link-button danger" data-delete-student="${esc(s.id)}" title="Permanently delete student account">Delete</button>
                    </td>
                  </tr>
                `).join('') || '<tr><td colspan="6" style="text-align:center;padding:30px;color:var(--muted)">No student accounts found. Click "+ Add student" or "Bulk import students".</td></tr>'}
              </tbody>
            </table>
          </div>
        </section>
        <p class="helper" style="margin:12px 2px">Accounts are administrator-provisioned. Students cannot self-register or change their assigned domain.</p>
      </div>
    `;
  }


  function assessmentsPage() {
    return `
      <div class="page">
        ${pageHead(
          'Scheduling',
          'Assessments',
          'Fixed start times, separate MCQ / coding pool draws, and one attempt per student.',
          `<button type="button" class="button primary" data-modal="assessment">＋ Schedule assessment</button>`
        )}

        <div class="notice" style="margin-bottom:15px">
          <strong>Schedule Timezone: India Standard Time (IST)</strong>
          The server enforces start times and deadlines. Late attempts receive only the remaining minutes.
        </div>

        <section class="card">
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Assessment</th>
                  <th>Domain</th>
                  <th>Start (IST)</th>
                  <th>Duration</th>
                  <th>MCQ Draw</th>
                  <th>Coding Draw</th>
                  <th>Assigned</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                ${state.assessments.map(a => `
                  <tr>
                    <td><strong>${esc(a.title)}</strong></td>
                    <td>${esc(a.domain)}</td>
                    <td>${fmt(a.starts_at)}</td>
                    <td>${a.duration_min} min</td>
                    <td>${a.mcq_count}</td>
                    <td>${a.coding_count}</td>
                    <td>${a.assigned ?? '—'} students</td>
                    <td>${pill(a.status, a.status === 'Scheduled' ? 'green' : a.status === 'Draft' ? 'amber' : 'gray')}</td>
                    <td>
                      <button type="button" class="link-button" data-edit-assessment="${a.id}">Edit</button>
                    </td>
                  </tr>
                `).join('') || '<tr><td colspan="9" style="text-align:center;padding:30px;color:var(--muted)">No assessments scheduled yet. Click "+ Schedule assessment".</td></tr>'}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    `;
  }

  function resultsPage() {
    return `
      <div class="page">
        ${pageHead(
          'Attempts',
          'Assessment results',
          'Server-recorded submissions, scores, and integrity signals.',
          `<button type="button" class="button secondary" data-action="export-results">↓ Export results (CSV / Google Sheets)</button>`
        )}

        <section class="card">
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Assessment</th>
                  <th>Domain</th>
                  <th>Started</th>
                  <th>Submitted</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Grading</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                ${state.results.map(r => `
                  <tr>
                    <td><strong>${esc(r.student)}</strong><div class="table-meta">${esc(r.student_id)}</div></td>
                    <td>${esc(r.assessment)}</td>
                    <td>${esc(r.domain)}</td>
                    <td>${fmt(r.started_at)}</td>
                    <td>${fmt(r.submitted_at)}</td>
                    <td>${pill(r.status, r.status === 'Submitted' ? 'green' : 'amber')}</td>
                    <td><strong>${r.score === null ? '—' : `${r.score} / ${r.max_score}`}</strong></td>
                    <td>${esc(r.grading_status)}</td>
                    <td>
                      <button type="button" class="link-button" data-result="${esc(r.id)}">View answers</button>
                    </td>
                  </tr>
                `).join('') || '<tr><td colspan="9" style="text-align:center;padding:30px;color:var(--muted)">No assessment attempts submitted yet.</td></tr>'}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    `;
  }

  function showResult(data) {
    const a = data.attempt;
    modal.innerHTML = `
      <div class="modal-inner wide">
        <div class="modal-head">
          <div>
            <h2>${esc(a.student)} · ${esc(a.assessment)}</h2>
            <p>${esc(a.student_id)} · ${esc(a.domain)} · Score: <strong>${a.score ?? '—'} / ${a.max_score ?? '—'}</strong> (${a.status})</p>
          </div>
          <button type="button" class="close-modal" data-action="close-modal">×</button>
        </div>
        <div class="assessment-list">
          ${data.answers.map((item, i) => {
            const q = item.question;
            const answer = item.answer;
            if (q.type === 'MCQ') {
              const selected = Number.isInteger(q.selectedOption) ? q.options[q.selectedOption] : 'Not answered';
              const correct = q.options['ABCD'.indexOf(q.correctOption)] || '—';
              return `
                <section class="card">
                  <div class="card-title">${i + 1}. ${esc(q.title)}</div>
                  <div class="table-meta">MCQ · ${pill(q.isCorrect ? 'Correct' : 'Incorrect', q.isCorrect ? 'green' : 'red')}</div>
                  <p style="margin:8px 0 4px">Student answer: <b>${esc(selected)}</b></p>
                  <p style="margin:0;color:var(--muted)">Correct answer: <b>${esc(correct)}</b></p>
                </section>
              `;
            }
            const language = answer?.language || '—';
            const code = answer?.drafts?.[language] || '';
            return `
              <section class="card">
                <div class="card-title">${i + 1}. ${esc(q.title)}</div>
                <div class="table-meta">Coding · ${esc(language)}</div>
                <pre style="white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f7f4;padding:12px;border-radius:9px;font-size:11px;margin-top:10px">${esc(code || 'Not answered')}</pre>
              </section>
            `;
          }).join('')}
        </div>
        <div class="modal-actions">
          <button type="button" class="button secondary" data-action="close-modal">Close</button>
        </div>
      </div>
    `;
    modal.classList.add('wide');
    modal.showModal();
  }

  function reviewPage() {
    return `
      <div class="page">
        ${pageHead('Integrity review', 'Review flags', 'Full-screen exits and tab visibility departures recorded for administrator audit.')}
        ${state.flags.length ? `
          <section class="card">
            <div class="table-wrap">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Assessment</th>
                    <th>Event</th>
                    <th>Detail</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  ${state.flags.map(f => `
                    <tr>
                      <td><strong>${esc(f.student)}</strong><div class="table-meta">${esc(f.student_id)}</div></td>
                      <td>${esc(f.assessment)}</td>
                      <td>${esc(f.event_type)}</td>
                      <td>${esc(f.detail)}</td>
                      <td>${fmt(f.created_at)}</td>
                      <td>${f.reviewed_at ? pill('Reviewed', 'green') : pill('Needs review', 'amber')}</td>
                      <td>
                        ${f.reviewed_at ? '' : `<button type="button" class="link-button" data-resolve-flag="${f.id}">Mark reviewed</button>`}
                      </td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </section>
        ` : `
          <section class="card empty-state">
            <strong>No review flags recorded</strong>
            Monitoring events will appear here when students trigger warnings during an exam.
          </section>
        `}
      </div>
    `;
  }

  function renderAdmin() {
    const pages = {
      Dashboard: adminDashboard,
      Domains: domainsPage,
      'Question bank': questionsPage,
      Students: studentsPage,
      Assessments: assessmentsPage,
      Results: resultsPage,
      'Review flags': reviewPage
    };
    shell((pages[state.page] || adminDashboard)());
  }

  function renderStudentHome() {
    const home = state.studentHome;
    const domain = home?.domain;

    app.innerHTML = `
      <div class="student-shell">
        <header class="student-top">
          <div class="brand">
            <div class="brand-mark">A</div>
            <div>
              <div class="brand-name">Assessment Portal</div>
              <div class="brand-sub">Student Workspace</div>
            </div>
          </div>
          <div class="student-top-right">
            <span class="timezone">IST · Asia/Kolkata</span>
            <button type="button" class="link-button" data-action="signout">Sign out</button>
          </div>
        </header>
        <div class="student-content">
          <div class="student-welcome">
            <div>
              <div class="eyebrow">Your workspace</div>
              <h1>Welcome, ${esc(state.user.name)}</h1>
              <p>Your assigned domain is <b>${esc(domain?.name || 'Assigned')}</b>. You can only access assessments in this domain.</p>
            </div>
            ${pill('Domain assigned', 'green')}
          </div>
          <div class="student-layout">
            <div>
              <section class="student-card next-assessment">
                <div class="next-label">Your assessments</div>
                ${home?.assessments?.length ? home.assessments.map(a => `
                  <article class="assessment-row">
                    <div class="assessment-mark">▣</div>
                    <div class="assessment-row-main">
                      <strong>${esc(a.title)}</strong>
                      <span>${fmt(a.starts_at)} · ${a.duration_min} min</span>
                      <span>${a.mcq_count} MCQ + ${a.coding_count} coding questions</span>
                    </div>
                    ${a.attempt?.status === 'In progress' ? `
                      <button type="button" class="button primary small" data-resume-attempt="${a.attempt.id}">Resume attempt →</button>
                    ` : a.attempt ? `
                      ${pill(a.attempt.status, a.attempt.status === 'Submitted' ? 'green' : 'gray')}
                    ` : `
                      <button type="button" class="button primary small" data-begin-assessment="${a.id}">Begin when open →</button>
                    `}
                  </article>
                `).join('') : '<div class="empty-state">No assessments scheduled for your domain at this time.</div>'}
              </section>

              <section class="student-card section-gap">
                <div class="card-title">Before you begin</div>
                <div class="info-row">
                  <span class="info-ico">◉</span>
                  <div>
                    <b>Camera is local preview only</b>
                    <span>Your camera feed stays in your browser and is never uploaded or recorded to any server.</span>
                  </div>
                </div>
                <div class="info-row">
                  <span class="info-ico">⚑</span>
                  <div>
                    <b>Browser integrity monitoring</b>
                    <span>Two tab visibility warnings are permitted. A third detected departure submits the test automatically.</span>
                  </div>
                </div>
                <div class="info-row">
                  <span class="info-ico">⌨</span>
                  <div>
                    <b>Clipboard restrictions</b>
                    <span>Copy, cut, and paste shortcuts are disabled inside the examination window.</span>
                  </div>
                </div>
              </section>
            </div>

            <div>
              <section class="student-card">
                <div class="card-title">Your profile</div>
                <div class="info-row">
                  <span class="info-ico">♙</span>
                  <div>
                    <b>${esc(state.user.name)}</b>
                    <span>Student ID: ${esc(state.user.id || state.user.email)}</span>
                  </div>
                </div>
                <div class="info-row">
                  <span class="info-ico">◈</span>
                  <div>
                    <b>${esc(domain?.name || '—')}</b>
                    <span>Assigned domain (${esc(domain?.category || '—')})</span>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  async function loadStudentHome() {
    const data = await api('/api/student/home');
    state.studentHome = data;
    if (window.location.pathname !== '/student/home') {
      history.pushState({ page: '__student__' }, '', '/student/home');
    }
    renderStudentHome();
  }

  function preflight(assessment) {
    app.innerHTML = `
      <div class="student-shell">
        <header class="student-top">
          <div class="brand">
            <div class="brand-mark">A</div>
            <div>
              <div class="brand-name">Assessment Portal</div>
              <div class="brand-sub">Device Readiness</div>
            </div>
          </div>
          <div class="student-top-right">${esc(assessment.title)} · ${assessment.duration_min} min</div>
        </header>
        <div class="student-content preflight">
          <div class="preflight-head">
            <div class="step">Assessment Check</div>
            <h1>Prepare your device</h1>
            <p>Complete the browser checks before beginning the scheduled test.</p>
          </div>
          <section class="student-card">
            <div class="checklist">
              <label class="check-item">
                <input type="checkbox" id="dndCheck">
                <span>
                  <strong>Turn on Do Not Disturb</strong>
                  <p>Silence notifications to prevent tab focus disruptions.</p>
                </span>
              </label>
              <label class="check-item">
                <input type="checkbox" id="appsCheck">
                <span>
                  <strong>Close other apps and tabs</strong>
                  <p>Keep the assessment page focused for the full exam duration.</p>
                </span>
              </label>
            </div>

            <div class="camera-box">
              <div class="camera-preview" id="cameraPreview"><span>Camera preview</span></div>
              <div class="camera-copy">
                <strong>Camera access · Local preview</strong>
                <p>The video preview runs locally on this device and is not saved or transmitted.</p>
                <div id="cameraStatus" class="camera-status">Camera permission not yet granted</div>
              </div>
              <button type="button" class="button secondary small" data-action="camera">Enable camera</button>
            </div>

            <label class="consent-line">
              <input id="consentCheck" type="checkbox">
              <span>I understand that full-screen is requested, tab visibility is monitored, the first two departures record warnings, and the third departure auto-submits. Copy and paste are blocked within this page.</span>
            </label>

            <div class="preflight-footer">
              <button type="button" class="button secondary" data-action="student-home">← Back</button>
              <button type="button" class="button primary" id="startExam" data-action="start-attempt" data-assessment="${assessment.id}" disabled>Start assessment →</button>
            </div>
          </section>
        </div>
      </div>
    `;

    if (state.camera) {
      const v = $('#cameraPreview');
      if (v) {
        v.innerHTML = '<video autoplay muted playsinline></video>';
        v.querySelector('video').srcObject = state.camera;
        $('#cameraStatus').textContent = 'Camera active · Local preview';
      }
    }
    updateStart();
  }

  function updateStart() {
    const b = $('#startExam');
    if (b) {
      const cameraOk = state.camera?.getVideoTracks().some(t => t.readyState === 'live');
      const dndOk = $('#dndCheck')?.checked;
      const appsOk = $('#appsCheck')?.checked;
      const consentOk = $('#consentCheck')?.checked;
      b.disabled = !(cameraOk && dndOk && appsOk && consentOk);
    }
  }

  function examView() {
    const ex = state.attempt;
    const q = ex.questions[state.index];
    const answer = q.answer || {};
    const lang = (q.languages || []).includes(answer.language) ? answer.language : (q.languages || [])[0];

    const deadlineMs = Date.parse(ex.attempt.deadline_at);
    const totalSecsLeft = Math.max(0, Math.floor((deadlineMs - Date.now()) / 1000));
    const mins = Math.floor(totalSecsLeft / 60);
    const secs = totalSecsLeft % 60;

    app.innerHTML = `
      <div class="exam-shell">
        <header class="exam-bar">
          <div class="exam-brand">Assessment Portal</div>
          <div class="exam-progress">
            <div class="exam-progress-label">
              <span>Question ${state.index + 1} of ${ex.questions.length}</span>
              <span>${ex.questions.filter(x => x.answer !== null && x.answer !== undefined).length} answered</span>
            </div>
            <div class="progress-line">
              <span style="width:${((state.index + 1) / ex.questions.length) * 100}%"></span>
            </div>
          </div>
          <div id="timer" class="exam-timer ${mins < 5 ? 'warning' : ''}">
            ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}
          </div>
          <button type="button" class="button secondary small" data-action="submit-attempt">Submit test</button>
        </header>

        <main class="exam-main">
          <section class="question-card">
            <div id="eventNotice" class="event-banner" ${state.tabEvents ? '' : 'hidden'}>
              ⚑ ${state.tabEvents < 3 ? `Warning ${state.tabEvents} of 2 · Tab departure recorded.` : 'Attempt auto-submitted.'}
            </div>
            <div class="question-meta">
              ${pill(q.type, q.type === 'Coding' ? 'amber' : 'gray')}
              ${pill(state.studentHome?.domain?.name || 'Domain', 'green')}
            </div>
            <h1 class="question-text">${esc(q.title)}</h1>

            ${q.type === 'MCQ' ? `
              <div class="option-list">
                ${q.options.map((o, i) => `
                  <label class="option ${answer.optionIndex === i ? 'selected' : ''}" data-option="${i}">
                    <span class="option-letter">${'ABCD'[i]}</span>
                    <span>${esc(o)}</span>
                  </label>
                `).join('')}
              </div>
            ` : `
              <div class="field">
                <label for="codeLanguage">Programming Language</label>
                <select id="codeLanguage">
                  ${q.languages.map(l => `<option ${lang === l ? 'selected' : ''}>${esc(l)}</option>`).join('')}
                </select>
                <textarea class="code-answer" id="codeAnswer" rows="15" placeholder="Read from standard input and write to standard output...">${esc(answer.drafts?.[lang] ?? q.starterCodes?.[lang] ?? '')}</textarea>
                <div style="display:flex;gap:8px;margin-top:8px;align-items:center">
                  <button type="button" class="button secondary small" data-action="run-code">Run sample tests</button>
                  <span class="helper">Code execution requires the isolated runner Docker container.</span>
                </div>
                <div id="runResults" style="margin-top:10px"></div>
              </div>
            `}

            <div class="question-nav">
              <button type="button" class="button secondary" data-action="prev-question" ${state.index === 0 ? 'disabled' : ''}>← Previous</button>
              <button type="button" class="button primary" data-action="next-question">
                ${state.index === ex.questions.length - 1 ? 'Review & finish' : 'Save & continue →'}
              </button>
            </div>
          </section>

          <aside class="exam-side">
            <section class="side-card">
              <h3>Question navigator</h3>
              <div class="question-map">
                ${ex.questions.map((x, i) => `
                  <button type="button" class="qmap-btn ${i === state.index ? 'current' : ''} ${x.answer ? 'answered' : ''}" data-index="${i}">${i + 1}</button>
                `).join('')}
              </div>
              <div class="legend"><i></i> Answered &nbsp;&nbsp; ○ Not answered</div>
            </section>
            <section class="side-card">
              <h3>Assessment details</h3>
              <div class="helper">
                <b>${esc(ex.attempt.assessment_title || 'Assessment')}</b><br>
                Autosaved continuously<br>
                Departures: ${state.tabEvents} / 3
              </div>
            </section>
          </aside>
        </main>

        <aside class="camera-pip">
          <video id="examCamera" autoplay muted playsinline></video>
          <span class="camera-pip-status"><i></i>Camera active · Local preview</span>
        </aside>
      </div>
    `;

    const video = $('#examCamera');
    if (video && state.camera) {
      video.srcObject = state.camera;
      video.play().catch(() => {});
    }

    if (!state.timer) {
      state.timer = setInterval(tick, 1000);
    }
  }

  async function saveAnswer() {
    if (!state.attempt) return;
    const q = state.attempt.questions[state.index];
    if (!q || q.type === 'MCQ') return;
    const language = $('#codeLanguage')?.value || q.languages[0];
    const code = $('#codeAnswer')?.value ?? '';
    q.answer = {
      language,
      drafts: {
        ...(q.answer?.drafts || {}),
        [language]: code
      }
    };
    await api(`/api/student/attempts/${encodeURIComponent(state.attempt.attempt.id)}/answers/${encodeURIComponent(q.id)}`, {
      method: 'PUT',
      body: JSON.stringify({ answer: q.answer })
    });
  }

  async function tick() {
    if (!state.attempt) return;
    const left = Math.floor((Date.parse(state.attempt.attempt.deadline_at) - Date.now()) / 1000);
    const n = $('#timer');
    if (n) {
      const mins = Math.max(0, Math.floor(left / 60));
      const secs = Math.max(0, left % 60);
      n.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      if (left < 300) n.classList.add('warning');
    }
    if (left <= 0) {
      await submitAttempt('Time expired');
    }
  }

  async function submitAttempt(reason = 'Student submitted') {
    if (!state.attempt) return;
    try {
      if (state.attempt.questions[state.index]?.type === 'Coding') {
        await saveAnswer().catch(() => {});
      }
      const attemptId = state.attempt.attempt.id;
      const result = await post(`/api/student/attempts/${encodeURIComponent(attemptId)}/submit`, { reason });

      // Live Google Sheets webhook sync if configured
      const webhookUrl = localStorage.getItem('ap_sheets_webhook');
      if (webhookUrl) {
        fetch(webhookUrl, {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student: state.user?.name,
            studentId: state.user?.id,
            assessment: state.attempt.attempt.assessment_title,
            reason,
            submittedAt: new Date().toISOString()
          })
        }).catch(() => {});
      }

      clearInterval(state.timer);
      state.timer = null;
      state.attempt = null;
      clearCamera();
      if (document.fullscreenElement) {
        await document.exitFullscreen().catch(() => {});
      }
      renderSubmitted(reason);
      toast('Assessment submitted successfully.');
    } catch (e) {
      toast(e.message);
    }
  }

  function renderSubmitted(reason) {
    app.innerHTML = `
      <div class="student-shell">
        <header class="student-top">
          <div class="brand">
            <div class="brand-mark">A</div>
            <div>
              <div class="brand-name">Assessment Portal</div>
              <div class="brand-sub">Submission Confirmed</div>
            </div>
          </div>
        </header>
        <div class="submit-confirm">
          <div class="submit-check">✓</div>
          <h1>Assessment submitted</h1>
          <p>${esc(reason)}</p>
          <p class="helper">Your answers have been recorded securely on the server.</p>
          <button type="button" class="button primary" data-action="student-home" style="margin-top:15px">Return to student home →</button>
        </div>
      </div>
    `;
  }

  function renderStudent() {
    if (state.attempt) return examView();
    if (state.preflightAssessment) return preflight(state.preflightAssessment);
    renderStudentHome();
  }

  function render() {
    if (!state.user) return renderLogin();
    if (state.user.role === 'admin') return renderAdmin();
    return renderStudent();
  }

  function toLocalInput(iso) {
    try {
      const d = new Date(iso);
      const parts = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hourCycle: 'h23'
      }).formatToParts(d);
      const v = Object.fromEntries(parts.map(p => [p.type, p.value]));
      return `${v.year}-${v.month}-${v.day}T${v.hour}:${v.minute}`;
    } catch (_) {
      return '';
    }
  }

  function modalForm(type, record = null) {
    let title = '';
    let body = '';

    if (type === 'domain') {
      title = record ? 'Edit domain' : 'Add a domain';
      body = `
        ${field('Domain name', 'name', record?.name || '', 'text', 'required maxlength="100" placeholder="e.g. Full Stack Python"')}
        <div class="field">
          <label>Category</label>
          <select name="category" required>
            <option ${record?.category === 'Software' ? 'selected' : ''}>Software</option>
            <option ${record?.category === 'Electrical / Electronics' ? 'selected' : ''}>Electrical / Electronics</option>
          </select>
        </div>
        ${field('Icon symbol', 'icon', record?.icon || '◈', 'text', 'maxlength="8"')}
        <div class="field full-width">
          <label>Description</label>
          <textarea name="description" placeholder="Brief overview of skills evaluated in this domain">${esc(record?.description || '')}</textarea>
        </div>
        ${record ? `
          <div class="field">
            <label>Status</label>
            <select name="status">
              <option ${record.status === 'Active' ? 'selected' : ''}>Active</option>
              <option ${record.status === 'Archived' ? 'selected' : ''}>Archived</option>
            </select>
          </div>
        ` : ''}
      `;
    }

    if (type === 'question') {
      title = record?.id ? 'Edit question' : 'Add question';
      const qtype = record?.type || 'MCQ';
      const qdata = record?.data || record || {};
      const codingDefaults = {
        languages: qdata.languages || ['Python'],
        starterCodes: qdata.starterCodes || { Python: 'value = input()\nprint(value)' },
        sampleTests: qdata.sampleTests || [{ input: 'hello', output: 'hello' }],
        hiddenTests: qdata.hiddenTests || [{ input: 'test', output: 'test' }],
        timeLimitSeconds: qdata.timeLimitSeconds || 3,
        memoryLimitMB: qdata.memoryLimitMB || 256
      };

      body = `
        <div class="field">
          <label>Domain</label>
          <select name="domainId" required>
            ${state.domains.filter(d => d.status === 'Active' || d.id === record?.domain_id).map(d => `
              <option value="${d.id}" ${(record?.domain_id || record?.domainId) === d.id ? 'selected' : ''}>${esc(d.name)}</option>
            `).join('')}
          </select>
        </div>
        <div class="field">
          <label>Question type</label>
          <select name="type" id="questionType">
            <option ${qtype === 'MCQ' ? 'selected' : ''}>MCQ</option>
            <option ${qtype === 'Coding' ? 'selected' : ''}>Coding</option>
          </select>
        </div>
        <div class="field">
          <label>Difficulty</label>
          <select name="difficulty">
            ${['Easy', 'Medium', 'Hard'].map(x => `<option ${record?.difficulty === x ? 'selected' : ''}>${x}</option>`).join('')}
          </select>
        </div>
        <div class="field full-width">
          <label>Question prompt</label>
          <textarea name="title" required rows="3" placeholder="Enter problem statement or question text">${esc(record?.title || '')}</textarea>
        </div>

        <div id="mcqFields" class="full-width" style="display:grid;grid-template-columns:1fr 1fr;gap:13px">
          <div class="field full-width">
            <label>Options (one per line, 2 to 4 options)</label>
            <textarea name="options" rows="4" placeholder="Option A&#10;Option B&#10;Option C&#10;Option D">${esc((qdata.options || ['Option A', 'Option B']).join('\n'))}</textarea>
          </div>
          <div class="field">
            <label>Correct option</label>
            <select name="correctOption">
              ${['A', 'B', 'C', 'D'].map(x => `<option ${qdata.correctOption === x ? 'selected' : ''}>${x}</option>`).join('')}
            </select>
          </div>
        </div>

        <div id="codingFields" class="full-width" style="display:grid;grid-template-columns:1fr 1fr;gap:13px">
          <div class="field full-width">
            <label>Supported languages</label>
            <div class="checklist" style="display:flex;gap:10px;flex-wrap:wrap">
              ${supportedLanguages.map(l => `
                <label class="check-item" style="padding:8px 12px">
                  <input type="checkbox" name="languages" value="${l}" ${(codingDefaults.languages || []).includes(l) ? 'checked' : ''}>
                  <span><strong>${l}</strong></span>
                </label>
              `).join('')}
            </div>
          </div>
          <div class="field full-width">
            <label>Starter code by language (JSON object)</label>
            <textarea name="starterCodes" rows="4">${esc(JSON.stringify(codingDefaults.starterCodes, null, 2))}</textarea>
          </div>
          <div class="field">
            <label>Public sample tests (JSON array of {input, output})</label>
            <textarea name="sampleTests" rows="3">${esc(JSON.stringify(codingDefaults.sampleTests, null, 2))}</textarea>
          </div>
          <div class="field">
            <label>Private hidden grading tests (JSON array)</label>
            <textarea name="hiddenTests" rows="3">${esc(JSON.stringify(codingDefaults.hiddenTests, null, 2))}</textarea>
          </div>
          <div class="field">
            <label>Time limit (seconds)</label>
            <input name="timeLimitSeconds" type="number" min="1" max="30" value="${codingDefaults.timeLimitSeconds}">
          </div>
          <div class="field">
            <label>Memory limit (MB)</label>
            <input name="memoryLimitMB" type="number" min="32" max="2048" value="${codingDefaults.memoryLimitMB}">
          </div>
        </div>
      `;
    }

    if (type === 'student') {
      title = record ? 'Edit student' : 'Provision a student';
      body = `
        ${field('Student ID', 'id', record?.id || '', 'text', record ? 'readonly required' : 'required placeholder="e.g. ST-20418"')}
        ${field('Full name', 'name', record?.name || '', 'text', 'required placeholder="e.g. John Doe"')}
        ${field('Email address', 'email', record?.email || '', 'email', 'required placeholder="e.g. student@company.com"')}
        <div class="field">
          <label>Assigned domain</label>
          <select name="domainId" required>
            ${state.domains.filter(d => d.status === 'Active' || d.id === record?.domain_id).map(d => `
              <option value="${d.id}" ${(record?.domain_id || record?.domainId) === d.id ? 'selected' : ''}>${esc(d.name)}</option>
            `).join('')}
          </select>
        </div>
        <div class="field full-width">
          <label>${record ? 'New password (leave blank to keep current)' : 'Password (optional — default is studentID@2026, min 6 chars)'}</label>
          <input type="text" name="password" autocomplete="new-password" placeholder="${record ? 'Leave blank to keep current' : 'e.g. Secret123 or leave blank to auto-generate'}">
          <span class="helper">${record ? 'Leave blank unless you wish to reset the password.' : 'Leave blank to automatically generate a temporary password (e.g. ST-101 -> st-101@2026).'}</span>
        </div>
      `;
    }

    if (type === 'bulk-student') {
      title = 'Bulk import students (CSV / Google Sheets)';
      body = `
        <div class="toolbar" style="margin-bottom:12px">
          <button type="button" class="button secondary small" data-action="download-student-template">↓ Download template</button>
          <label class="button secondary small" for="studentBulkFile">Choose CSV file</label>
          <input id="studentBulkFile" type="file" accept=".csv,text/csv" hidden>
        </div>
        <div class="field full-width">
          <label>Google Sheets CSV URL or Paste CSV data</label>
          <div style="display:flex;gap:6px;margin-bottom:8px">
            <input type="url" id="studentSheetsUrl" placeholder="Paste published Google Sheets CSV link (https://docs.google.com/.../pub?output=csv)">
            <button type="button" class="button secondary small" data-action="load-student-sheets-url">Fetch</button>
          </div>
          <textarea name="csv" id="studentCsvText" rows="10" placeholder="id,name,email,domainId,password&#10;ST-101,Aarav Sharma,aarav@test.invalid,1,Welcome@2026!"></textarea>
          <span class="helper">Columns: id, name, email, domainId (or domain name), password (optional, auto-generated if blank).</span>
        </div>
      `;
    }

    if (type === 'bulk') {
      title = 'Bulk import questions (CSV / Google Sheets)';
      body = `
        <div class="toolbar" style="margin-bottom:12px">
          <button type="button" class="button secondary small" data-action="download-template">↓ Download template</button>
          <label class="button secondary small" for="bulkFile">Choose CSV file</label>
          <input id="bulkFile" type="file" accept=".csv,text/csv" hidden>
        </div>
        <div class="field full-width">
          <label>Google Sheets CSV URL or Paste CSV data</label>
          <div style="display:flex;gap:6px;margin-bottom:8px">
            <input type="url" id="sheetsUrl" placeholder="Paste published Google Sheets CSV link (https://docs.google.com/.../pub?output=csv)">
            <button type="button" class="button secondary small" data-action="load-sheets-url">Fetch</button>
          </div>
          <textarea name="csv" id="bulkCsvText" rows="11" placeholder="domainId,type,title,difficulty,options,correctOption,languages,starterCodes,sampleTests,hiddenTests,timeLimitSeconds,memoryLimitMB"></textarea>
          <span class="helper">MCQ options use | as separator. For coding, set domainId as "General" or leave blank; test cases can be written as "4 -&gt; 16 | 5 -&gt; 25".</span>
        </div>
      `;
    }

    if (type === 'assessment') {
      title = record ? 'Edit assessment' : 'Schedule assessment';
      body = `
        ${field('Assessment title', 'title', record?.title || '', 'text', 'required placeholder="e.g. Java Mid-Term Evaluation"')}
        <div class="field">
          <label>Domain</label>
          <select name="domainId" required>
            ${state.domains.filter(d => d.status === 'Active' || d.id === record?.domain_id).map(d => `
              <option value="${d.id}" ${(record?.domain_id || record?.domainId) === d.id ? 'selected' : ''}>${esc(d.name)}</option>
            `).join('')}
          </select>
        </div>
        ${field('MCQ question count', 'mcqCount', record?.mcq_count ?? 5, 'number', 'min="0" required')}
        ${field('Coding question count', 'codingCount', record?.coding_count ?? 1, 'number', 'min="0" required')}
        ${field('Start date & time (IST)', 'startsAt', record?.starts_at ? toLocalInput(record.starts_at) : '', 'datetime-local', 'required')}
        ${field('Duration (minutes)', 'durationMinutes', record?.duration_min || 45, 'number', 'min="5" max="240" required')}
        <div class="field">
          <label>Status</label>
          <select name="status">
            <option ${record?.status === 'Scheduled' || !record ? 'selected' : ''}>Scheduled</option>
            <option ${record?.status === 'Draft' ? 'selected' : ''}>Draft</option>
            <option ${record?.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
          </select>
        </div>
      `;
    }

    if (type === 'sheets-sync') {
      title = 'Google Sheets Live Sync Configuration';
      const existing = state.sheetsConfig?.webhookUrl || localStorage.getItem('ap_sheets_webhook') || '';
      const isConfigured = Boolean(state.sheetsConfig?.configured || existing);
      const retentionDays = state.retentionDays || 90;
      body = `
        <div class="notice full-width" style="margin-bottom:14px;background:#f0f9f4;border-color:#bce5cf;color:#185e4b">
          <strong>Status: ${isConfigured ? '● Connected to Google Sheets' : '○ Not yet connected'}</strong>
          <p style="margin:4px 0 0 0">Whenever a student, domain, question, assessment, or result is created or submitted, it is saved in SQLite and synchronized to Google Sheets in real time.</p>
        </div>
        <div class="field full-width">
          <label>Google Apps Script Web App URL</label>
          <input type="url" name="sheetsWebhook" value="${esc(existing)}" placeholder="https://script.google.com/macros/s/.../exec">
          <span class="helper">Deploy the Google Apps Script Web App (see README for script) with "Execute as: Me" and "Who has access: Anyone", then paste the URL here.</span>
        </div>
        <div class="field full-width" style="padding-top:10px;border-top:1px solid var(--border);margin-top:8px">
          <label>Storage Auto-Cleanup & Data Retention (Days)</label>
          <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:4px">
            <input type="number" name="retentionDays" min="1" max="3650" value="${retentionDays}" style="max-width:140px">
            <span style="font-size:12px;color:var(--muted)">days before auto-purge</span>
            <button type="button" class="button secondary small" data-action="trigger-cleanup" style="color:var(--red,#c53030);border-color:#fed7d7;margin-left:auto">🗑 Run Cleanup Now</button>
          </div>
          <span class="helper" style="margin-top:6px;display:block">Completed/expired attempts and expired sessions older than this window are automatically purged daily to keep local SQLite storage lean. All master records remain permanent in Google Sheets.</span>
        </div>
        ${isConfigured ? `
          <div class="field full-width" style="padding-top:10px;border-top:1px solid var(--border);margin-top:8px">
            <label>Master Synchronization Controls</label>
            <p style="margin:0 0 10px 0;font-size:13px;color:var(--muted)">Manage two-way sync between your Google Sheet and the portal workspace.</p>
            <div style="display:flex;gap:10px;flex-wrap:wrap">
              <button type="button" class="button secondary" data-action="trigger-sheets-sync" style="font-weight:600">⚡ Push All Data to Google Sheets</button>
              <button type="button" class="button secondary" data-action="trigger-sheets-pull" style="font-weight:600">↓ Pull & Restore from Google Sheets</button>
            </div>
          </div>
        ` : ''}
      `;
    }

    const isWide = ['question', 'bulk', 'bulk-student'].includes(type);

    modal.innerHTML = `
      <form class="modal-inner ${isWide ? 'wide' : ''}" id="modalForm" data-type="${type}" data-id="${esc(record?.id || '')}">
        <div class="modal-head">
          <div>
            <h2>${title}</h2>
            <p>${type === 'student' ? 'Student accounts are admin-managed.' : type === 'bulk' || type === 'bulk-student' ? 'Bulk import data from CSV or Google Sheets.' : 'Configure this record for your portal workspace.'}</p>
          </div>
          <button type="button" class="close-modal" data-action="close-modal">×</button>
        </div>
        <div id="modalNotice" class="modal-notice" hidden></div>
        <div class="form-grid">
          ${body}
        </div>
        <div class="modal-actions">
          <button type="button" class="button secondary" data-action="close-modal">Cancel</button>
          <button type="submit" class="button primary">${record ? 'Save changes' : 'Save'}</button>
        </div>
      </form>
    `;

    modal.classList.toggle('wide', isWide);
    modal.showModal();

    if (type === 'question') {
      const sync = () => {
        const isCoding = $('#questionType')?.value === 'Coding';
        const mcqBox = $('#mcqFields');
        const codeBox = $('#codingFields');
        if (mcqBox) mcqBox.style.display = isCoding ? 'none' : 'grid';
        if (codeBox) codeBox.style.display = isCoding ? 'grid' : 'none';
      };
      $('#questionType')?.addEventListener('change', sync);
      sync();
    }
  }

  function showSignOutModal() {
    clearModalError();
    modal.classList.remove('wide');
    modal.classList.add('confirm-modal');
    modal.innerHTML = `
      <div class="signout-dialog">
        <button type="button" class="signout-close" data-action="close-modal" title="Cancel">✕</button>
        <div class="signout-icon-badge">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </div>
        <h2 class="signout-title">Sign out of Assessment Portal?</h2>
        <p class="signout-desc">
          Are you sure you want to end your current session? You will need your credentials to sign in again.
        </p>

        <div class="signout-profile-card">
          <div class="signout-avatar">
            ${esc((state.user?.name || 'U').slice(0, 2).toUpperCase())}
          </div>
          <div class="signout-info">
            <div class="signout-name-row">
              <span class="signout-name">${esc(state.user?.name || 'Current User')}</span>
              <span class="signout-role-pill">${esc(state.user?.role || 'Admin')}</span>
            </div>
            <div class="signout-email">${esc(state.user?.email || state.user?.id || '')}</div>
          </div>
        </div>

        <div class="signout-btn-row">
          <button type="button" class="btn-signout-cancel" data-action="close-modal">Cancel</button>
          <button type="button" class="btn-signout-confirm btn-danger-signout" data-action="confirm-signout" style="flex: 1.15; padding: 11px 16px; border-radius: 11px; background: linear-gradient(135deg, #e11d48, #be123c); border: 1px solid #be123c; color: #ffffff; font-weight: 700; font-size: 13px; cursor: pointer; box-shadow: 0 4px 14px rgba(225, 29, 72, 0.28); display: inline-flex; align-items: center; justify-content: center; gap: 7px; outline: none;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span>Yes, Sign out</span>
          </button>
        </div>
      </div>
    `;
    modal.showModal();
  }

  function parseTests(value, label) {
    if (!value || (typeof value === 'string' && !value.trim())) return [];
    if (Array.isArray(value)) return value;
    if (typeof value === 'string') {
      const trimmed = value.trim();
      if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
        try {
          const x = JSON.parse(trimmed);
          if (Array.isArray(x)) return x;
        } catch (_) {}
      }
      // Parse human-friendly arrow syntax: "input -> output | input -> output" or multiline
      const parts = trimmed.split(/[\r\n|]+/).map(p => p.trim()).filter(Boolean);
      const tests = [];
      for (const part of parts) {
        if (part.includes('->')) {
          const [inp, outp] = part.split('->').map(s => s.trim());
          tests.push({ input: inp ?? '', output: outp ?? '' });
        } else if (part.includes(':')) {
          const [inp, outp] = part.split(':').map(s => s.trim());
          tests.push({ input: inp ?? '', output: outp ?? '' });
        } else {
          tests.push({ input: part, output: part });
        }
      }
      if (tests.length > 0) return tests;
    }
    throw new Error(`${label} must be a valid JSON array or arrow syntax (e.g. 4 -> 16 | 5 -> 25).`);
  }

  function csvRows(text) {
    const rows = [];
    let row = [];
    let cell = '';
    let quoted = false;

    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (quoted) {
        if (c === '"' && text[i + 1] === '"') {
          cell += '"';
          i++;
        } else if (c === '"') {
          quoted = false;
        } else {
          cell += c;
        }
      } else if (c === '"') {
        quoted = true;
      } else if (c === ',') {
        row.push(cell);
        cell = '';
      } else if (c === '\n') {
        row.push(cell);
        if (row.some(x => x.trim())) rows.push(row);
        row = [];
        cell = '';
      } else if (c !== '\r') {
        cell += c;
      }
    }

    row.push(cell);
    if (row.some(x => x.trim())) rows.push(row);
    if (rows.length < 2) throw new Error('CSV must contain a header and at least one record.');

    const headers = rows.shift().map(h => h.trim());
    return rows.map((cells, i) => ({
      row: i + 2,
      values: Object.fromEntries(headers.map((h, j) => [h, (cells[j] || '').trim()]))
    }));
  }

  function parseBulkQuestionsCsv(text) {
    const parsed = csvRows(String(text || ''));
    const items = [];

    for (const { row, values: v } of parsed) {
      const fail = msg => { throw new Error(`Row ${row}: ${msg}`); };

      const type = String(v.type || '').toUpperCase() === 'CODING' ? 'Coding' : 'MCQ';

      let domain = state.domains.find(d => String(d.id) === v.domainId || d.name.toLowerCase() === String(v.domainId || '').toLowerCase());
      if (!domain && (type === 'Coding' || !v.domainId || ['general', 'common', 'all', '0', ''].includes(String(v.domainId || '').toLowerCase()))) {
        domain = state.domains.find(d => d.name.toLowerCase() === 'general') || state.domains[0];
      }
      if (!domain) fail(`domainId "${v.domainId}" must match an existing domain ID or name.`);

      const item = {
        domainId: domain.id,
        type,
        title: v.title || 'Untitled question',
        difficulty: ['Easy', 'Medium', 'Hard'].includes(v.difficulty) ? v.difficulty : 'Medium',
        data: {}
      };

      if (type === 'MCQ') {
        item.data.options = String(v.options || '').split('|').map(x => x.trim()).filter(Boolean);
        item.data.correctOption = String(v.correctOption || 'A').toUpperCase();
      } else {
        item.data.languages = String(v.languages || 'Python|Java').split('|').map(x => x.trim()).filter(Boolean);
        try {
          let starters = {};
          if (v.starterCodes && v.starterCodes.trim()) {
            if (v.starterCodes.trim().startsWith('{')) {
              starters = JSON.parse(v.starterCodes);
            } else {
              starters = { Python: v.starterCodes };
            }
          } else {
            starters = {
              Python: 'value = input()\nprint(value)',
              Java: 'import java.util.Scanner;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLine()) {\n            System.out.println(sc.nextLine());\n        }\n    }\n}'
            };
          }
          item.data.starterCodes = starters;
          item.data.sampleTests = parseTests(v.sampleTests, 'sampleTests');
          item.data.hiddenTests = parseTests(v.hiddenTests, 'hiddenTests');
        } catch (e) {
          fail(e.message);
        }
        item.data.timeLimitSeconds = Number(v.timeLimitSeconds || 3);
        item.data.memoryLimitMB = Number(v.memoryLimitMB || 256);
      }
      items.push(item);
    }
    return items;
  }


  function parseBulkStudentsCsv(text) {
    const parsed = csvRows(String(text || ''));
    const students = [];

    for (const { row, values: v } of parsed) {
      const fail = msg => { throw new Error(`Row ${row}: ${msg}`); };
      if (!v.id) fail('Missing student ID.');
      if (!v.name) fail('Missing student name.');
      if (!v.email) fail('Missing student email.');

      const dval = v.domainId || v.domain;
      const domain = state.domains.find(d => String(d.id) === String(dval) || d.name.toLowerCase() === String(dval || '').toLowerCase());
      if (!domain) fail(`Domain "${dval}" was not found.`);

      students.push({
        id: v.id,
        name: v.name,
        email: v.email,
        domainId: domain.id,
        password: v.password || undefined
      });
    }
    return students;
  }

  function downloadCsv(filename, rows) {
    const csvContent = rows.map(r => r.map(x => {
      const s = String(x ?? '');
      return /[",\r\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
    }).join(',')).join('\r\n') + '\r\n';

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  function downloadQuestionTemplate() {
    const rows = [
      ['domainId', 'type', 'title', 'difficulty', 'options', 'correctOption', 'languages', 'starterCodes', 'sampleTests', 'hiddenTests', 'timeLimitSeconds', 'memoryLimitMB'],
      [state.domains[0]?.id || '1', 'MCQ', 'Which keyword creates a constant in JavaScript?', 'Easy', 'var|let|const|def', 'C', '', '', '', '', '', ''],
      ['General', 'Coding', 'Read one integer and print its square.', 'Easy', '', '', 'Python|Java', '', '4 -> 16 | 5 -> 25', '7 -> 49 | 10 -> 100', '3', '256']
    ];
    downloadCsv('questions-template.csv', rows);
  }

  function downloadStudentTemplate() {
    const rows = [
      ['id', 'name', 'email', 'domainId', 'password'],
      ['ST-101', 'Aarav Sharma', 'aarav@company.test', state.domains[0]?.id || '1', 'Welcome@2026!'],
      ['ST-102', 'Priya Patel', 'priya@company.test', state.domains[0]?.id || '1', '']
    ];
    downloadCsv('students-template.csv', rows);
  }

  function exportResultsCsv() {
    if (!state.results.length) return toast('No results available to export.');
    const header = ['Student ID', 'Student Name', 'Assessment', 'Domain', 'Status', 'Score', 'Max Score', 'Percentage', 'Grading Status', 'Started At (IST)', 'Submitted At (IST)', 'Submit Reason'];
    const rows = [header, ...state.results.map(r => [
      r.student_id,
      r.student,
      r.assessment,
      r.domain,
      r.status,
      r.score ?? '',
      r.max_score ?? '',
      r.score !== null && r.max_score ? `${Math.round((r.score / r.max_score) * 100)}%` : '',
      r.grading_status,
      fmt(r.started_at),
      fmt(r.submitted_at),
      r.submit_reason || ''
    ])];
    downloadCsv(`assessment-results-${new Date().toISOString().slice(0, 10)}.csv`, rows);
    toast('Results exported to CSV for Google Sheets.');
  }

  function exportQuestionsCsv() {
    if (!state.questions.length) return toast('No questions to export.');
    const header = ['id', 'domainId', 'domain', 'type', 'difficulty', 'title', 'status', 'options', 'correctOption', 'languages'];
    const rows = [header, ...state.questions.map(q => {
      const dName = state.domains.find(d => d.id === q.domain_id)?.name || '';
      const opts = (q.data?.options || q.options || []).join('|');
      const correct = q.data?.correctOption || q.correctOption || '';
      const langs = (q.data?.languages || q.languages || []).join('|');
      return [q.id, q.domain_id, dName, q.type, q.difficulty, q.title, q.status, opts, correct, langs];
    })];
    downloadCsv('question-bank.csv', rows);
    toast('Question bank exported to CSV.');
  }

  function exportStudentsCsv() {
    if (!state.students.length) return toast('No students to export.');
    const header = ['id', 'name', 'email', 'domainId', 'domain', 'status'];
    const rows = [header, ...state.students.map(s => [
      s.id,
      s.name,
      s.email,
      s.domain_id,
      s.domain || state.domains.find(d => d.id === s.domain_id)?.name || '',
      s.status
    ])];
    downloadCsv('students.csv', rows);
    toast('Students list exported to CSV.');
  }

  async function saveModal(form) {
    const type = form.dataset.type;
    const id = form.dataset.id;
    const fd = new FormData(form);
    const v = Object.fromEntries(fd.entries());

    if (type === 'sheets-sync') {
      const url = (v.sheetsWebhook || '').trim();
      const retDays = parseInt(v.retentionDays, 10);

      // Save retention days
      if (!isNaN(retDays) && retDays >= 1 && retDays <= 3650) {
        const retRes = await post('/api/admin/settings/retention', { retentionDays: retDays });
        state.retentionDays = retRes.retentionDays || retDays;
      }

      // Save sheets webhook
      const res = await post('/api/admin/sheets/config', { webhookUrl: url });
      state.sheetsConfig = { webhookUrl: res.webhookUrl, configured: res.configured };
      if (url) localStorage.setItem('ap_sheets_webhook', url);
      else localStorage.removeItem('ap_sheets_webhook');

      modal.close();
      await refreshAdmin();
      toast('Configuration saved successfully.');
      return;
    }

    if (type === 'bulk') {
      const questions = parseBulkQuestionsCsv(v.csv);
      const result = await post('/api/admin/questions/bulk', { questions });
      modal.close();
      await refreshAdmin();
      toast(`Successfully imported ${result.count} questions.`);
      return;
    }

    if (type === 'bulk-student') {
      const students = parseBulkStudentsCsv(v.csv);
      const result = await post('/api/admin/students/bulk', { students });
      modal.close();
      await refreshAdmin();
      toast(`Successfully provisioned ${result.count} students.`);
      return;
    }

    if (type === 'domain') {
      const existing = state.domains.find(d => String(d.id) === String(id));
      const record = {
        name: v.name?.trim(),
        category: v.category,
        icon: v.icon?.trim() || '◈',
        description: v.description?.trim() || '',
        status: v.status || existing?.status || 'Active'
      };
      await api(id ? `/api/admin/domains/${id}` : '/api/admin/domains', {
        method: id ? 'PATCH' : 'POST',
        body: JSON.stringify(record)
      });
    }

    if (type === 'student') {
      const record = {
        id: v.id?.trim(),
        name: v.name?.trim(),
        email: v.email?.trim(),
        domainId: Number(v.domainId),
        password: v.password ? v.password.trim() : undefined
      };
      const res = await api(id ? `/api/admin/students/${encodeURIComponent(id)}` : '/api/admin/students', {
        method: id ? 'PATCH' : 'POST',
        body: JSON.stringify(record)
      });
      modal.close();
      await refreshAdmin();
      if (res?.temporaryPassword) {
        toast(`Student ${record.name} added! Temp password: ${res.temporaryPassword}`);
      } else {
        toast(id ? `Student ${record.name} updated.` : `Student ${record.name} added.`);
      }
      return;
    }

    if (type === 'assessment') {
      let startsIso;
      if (v.startsAt.includes('+') || v.startsAt.endsWith('Z')) {
        startsIso = new Date(v.startsAt).toISOString();
      } else {
        const withSec = v.startsAt.length === 16 ? v.startsAt + ':00' : v.startsAt;
        startsIso = new Date(withSec + '+05:30').toISOString();
      }

      const record = {
        title: v.title?.trim(),
        domainId: Number(v.domainId),
        mcqCount: Number(v.mcqCount),
        codingCount: Number(v.codingCount),
        startsAt: startsIso,
        durationMinutes: Number(v.durationMinutes),
        status: v.status || 'Scheduled'
      };

      await api(id ? `/api/admin/assessments/${encodeURIComponent(id)}` : '/api/admin/assessments', {
        method: id ? 'PATCH' : 'POST',
        body: JSON.stringify(record)
      });
    }

    if (type === 'question') {
      const qtype = v.type;
      let data = {};

      if (qtype === 'MCQ') {
        const opts = String(v.options || '').split('\n').map(x => x.trim()).filter(Boolean);
        if (opts.length < 2 || opts.length > 4) {
          throw new Error('MCQ must have between 2 and 4 options.');
        }
        data = {
          options: opts,
          correctOption: v.correctOption
        };
      } else {
        const langs = fd.getAll('languages');
        if (!langs.length) {
          throw new Error('Please select at least one programming language.');
        }
        data = {
          languages: langs,
          starterCodes: JSON.parse(v.starterCodes || '{}'),
          sampleTests: parseTests(v.sampleTests, 'Sample tests'),
          hiddenTests: parseTests(v.hiddenTests, 'Hidden tests'),
          timeLimitSeconds: Number(v.timeLimitSeconds || 3),
          memoryLimitMB: Number(v.memoryLimitMB || 256)
        };
      }

      const record = {
        domainId: Number(v.domainId),
        type: qtype,
        title: v.title?.trim(),
        difficulty: v.difficulty,
        status: 'Published',
        data
      };

      await api(id ? `/api/admin/questions/${encodeURIComponent(id)}` : '/api/admin/questions', {
        method: id ? 'PATCH' : 'POST',
        body: JSON.stringify(record)
      });
    }

    modal.close();
    await refreshAdmin();
    toast(id ? 'Changes saved successfully.' : 'New record created successfully.');
  }

  function clearCamera() {
    if (state.camera) {
      state.camera.getTracks().forEach(t => t.stop());
      state.camera = null;
    }
  }

  async function doAction(action, target) {
    if (action === 'download-template') {
      downloadQuestionTemplate();
      return;
    }
    if (action === 'download-student-template') {
      downloadStudentTemplate();
      return;
    }
    if (action === 'export-results') {
      exportResultsCsv();
      return;
    }
    if (action === 'export-questions') {
      exportQuestionsCsv();
      return;
    }
    if (action === 'export-students') {
      exportStudentsCsv();
      return;
    }
    if (action === 'load-sheets-url') {
      const url = $('#sheetsUrl')?.value?.trim();
      if (!url) return toast('Please enter a published Google Sheets CSV URL.');
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error('Could not fetch the Google Sheet CSV.');
        const text = await res.text();
        $('#bulkCsvText').value = text;
        toast('Google Sheets CSV loaded into preview.');
      } catch (e) {
        toast('Error loading Google Sheet: ' + e.message);
      }
      return;
    }
    if (action === 'load-student-sheets-url') {
      const url = $('#studentSheetsUrl')?.value?.trim();
      if (!url) return toast('Please enter a published Google Sheets CSV URL.');
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error('Could not fetch the Google Sheet CSV.');
        const text = await res.text();
        $('#studentCsvText').value = text;
        toast('Google Sheets student CSV loaded into preview.');
      } catch (e) {
        toast('Error loading Google Sheet: ' + e.message);
      }
      return;
    }
    if (action === 'trigger-sheets-sync') {
      try {
        if (target) {
          target.disabled = true;
          target.textContent = 'Syncing data to Google Sheets...';
        }
        const res = await post('/api/admin/sheets/sync_all', {});
        toast(`Synced to Google Sheets: ${res.counts.domains} domains, ${res.counts.students} students, ${res.counts.questions} questions, ${res.counts.assessments} assessments, ${res.counts.results} results!`);
        modal.close();
      } catch (err) {
        toast(err.message);
      } finally {
        if (target) {
          target.disabled = false;
          target.textContent = '⚡ Push All Data to Google Sheets';
        }
      }
      return;
    }
    if (action === 'trigger-sheets-pull') {
      try {
        if (target) {
          target.disabled = true;
          target.textContent = 'Pulling data from Google Sheets...';
        }
        const res = await post('/api/admin/sheets/pull_all', {});
        toast(`Restored from Google Sheets: ${res.restored.domains} domains, ${res.restored.students} students!`);
        modal.close();
        await refreshAdmin();
      } catch (err) {
        toast(err.message);
      } finally {
        if (target) {
          target.disabled = false;
          target.textContent = '↓ Pull & Restore from Google Sheets';
        }
      }
      return;
    }
    if (action === 'trigger-cleanup') {
      try {
        if (target) {
          target.disabled = true;
          target.textContent = 'Running cleanup...';
        }
        const res = await post('/api/admin/cleanup', {});
        const d = res.deleted || {};
        toast(`Cleanup completed! Removed ${d.attempts || 0} old attempts, ${d.sessions || 0} expired sessions, ${d.review_events || 0} review events.`);
      } catch (err) {
        toast('Cleanup failed: ' + err.message);
      } finally {
        if (target) {
          target.disabled = false;
          target.textContent = '🗑 Run Cleanup Now';
        }
      }
      return;
    }
    if (action === 'fullscreen') {
      try {
        await document.documentElement.requestFullscreen();
      } catch (_) {
        toast('Full screen could not start. Please try from your browser controls.');
      }
      return;
    }
    if (action === 'signout') {
      showSignOutModal();
      return;
    }
    if (action === 'confirm-signout') {
      modal.close();
      try {
        await post('/api/auth/logout', {});
      } catch (_) {}
      clearCamera();
      clearInterval(state.timer);
      state.timer = null;
      state.user = null;
      state.csrf = '';
      state.attempt = null;
      toast('You have successfully signed out.');
      loginView();
      return;
    }
    if (action === 'close-modal') {
      modal.close();
      modal.classList.remove('confirm-modal');
      modal.classList.remove('wide');
      return;
    }
    if (action === 'menu') {
      $('.sidebar')?.classList.toggle('open');
      return;
    }
    if (action === 'student-home') {
      state.preflightAssessment = null;
      state.resumeAttemptId = null;
      clearCamera();
      await loadStudentHome();
      return;
    }
    if (action === 'camera') {
      try {
        state.camera = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        const box = $('#cameraPreview');
        if (box) {
          box.innerHTML = '<video autoplay muted playsinline></video>';
          box.querySelector('video').srcObject = state.camera;
        }
        const st = $('#cameraStatus');
        if (st) st.textContent = 'Camera active · Local preview';
        updateStart();
      } catch (e) {
        toast(e.name === 'NotAllowedError' ? 'Camera permission was denied in your browser settings.' : e.message);
      }
      return;
    }
    if (action === 'start-attempt') {
      const assessment = state.studentHome?.assessments?.find(a => a.id === target.dataset.assessment);
      if (!state.camera || !$('#consentCheck')?.checked) {
        return toast('Please enable the camera and accept the assessment terms first.');
      }
      try {
        await document.documentElement.requestFullscreen().catch(() => {});
        const data = state.resumeAttemptId
          ? await api(`/api/student/attempts/${encodeURIComponent(state.resumeAttemptId)}`)
          : await post('/api/student/attempts/start', { assessmentId: assessment.id });

        state.resumeAttemptId = null;
        state.attempt = data;
        state.tabEvents = data.attempt.visibility_events || 0;
        state.fullEvents = data.attempt.fullscreen_events || 0;
        state.preflightAssessment = null;
        state.index = 0;
        renderStudent();
      } catch (e) {
        if (document.fullscreenElement) {
          await document.exitFullscreen().catch(() => {});
        }
        toast(e.message);
      }
      return;
    }
    if (action === 'submit-attempt') {
      if (confirm('Are you ready to submit your test? You cannot return to this attempt once submitted.')) {
        await submitAttempt('Student confirmed submission');
      }
      return;
    }
    if (action === 'prev-question') {
      if (state.index > 0) {
        if (state.attempt.questions[state.index].type === 'Coding') {
          await saveAnswer().catch(() => {});
        }
        state.index--;
        examView();
      }
      return;
    }
    if (action === 'next-question') {
      if (state.attempt.questions[state.index].type === 'Coding') {
        try {
          await saveAnswer();
        } catch (e) {
          return toast(e.message);
        }
      }
      if (state.index < state.attempt.questions.length - 1) {
        state.index++;
        examView();
      } else {
        toast('Review your answers on the map, then click "Submit test" when finished.');
      }
      return;
    }
    if (action === 'run-code') {
      try {
        await saveAnswer();
        const q = state.attempt.questions[state.index];
        const answer = q.answer;
        const result = await post(`/api/student/attempts/${encodeURIComponent(state.attempt.attempt.id)}/run`, {
          questionId: q.id,
          language: answer.language,
          code: answer.drafts[answer.language]
        });
        $('#runResults').innerHTML = `
          <div class="notice" style="background:#eef6ef;border-color:#c8dfcc">
            <strong>${result.passed} / ${result.total} sample tests passed</strong>
            ${result.results.map((r, i) => `<div>Test ${i + 1}: ${r.passed ? '✓ Passed' : `✗ Failed ${r.error ? '· ' + esc(r.error) : ''}`}</div>`).join('')}
          </div>
        `;
      } catch (e) {
        $('#runResults').innerHTML = `
          <div class="notice" style="background:#fff6f6;border-color:#fedada;color:#9b2a22">
            <strong>Runner unavailable</strong>
            <div>${esc(e.message)}</div>
          </div>
        `;
      }
      return;
    }
  }

  // GLOBAL DOCUMENT EVENT LISTENERS: Catches events across both #app and #modal
  document.addEventListener('click', async e => {
    const nav = e.target.closest('[data-page]');
    if (nav) {
      await goPage(nav.dataset.page);
      return;
    }

    const modalBtn = e.target.closest('[data-modal]');
    if (modalBtn) {
      modalForm(modalBtn.dataset.modal);
      return;
    }

    const actionNode = e.target.closest('[data-action]');
    if (actionNode) {
      await doAction(actionNode.dataset.action, actionNode);
      return;
    }

    const begin = e.target.closest('[data-begin-assessment]');
    if (begin) {
      state.preflightAssessment = state.studentHome?.assessments?.find(a => a.id === begin.dataset.beginAssessment);
      preflight(state.preflightAssessment);
      return;
    }

    const resume = e.target.closest('[data-resume-attempt]');
    if (resume) {
      const attemptId = resume.dataset.resumeAttempt;
      state.preflightAssessment = state.studentHome?.assessments?.find(a => a.attempt?.id === attemptId);
      state.resumeAttemptId = attemptId;
      preflight(state.preflightAssessment);
      return;
    }

    const option = e.target.closest('[data-option]');
    if (option && state.attempt) {
      const q = state.attempt.questions[state.index];
      q.answer = { optionIndex: Number(option.dataset.option) };
      try {
        await api(`/api/student/attempts/${encodeURIComponent(state.attempt.attempt.id)}/answers/${encodeURIComponent(q.id)}`, {
          method: 'PUT',
          body: JSON.stringify({ answer: q.answer })
        });
        examView();
      } catch (err) {
        toast(err.message);
      }
      return;
    }

    const map = e.target.closest('[data-index]');
    if (map && state.attempt) {
      if (state.attempt.questions[state.index].type === 'Coding') {
        try {
          await saveAnswer();
        } catch (err) {
          toast(err.message);
          return;
        }
      }
      state.index = Number(map.dataset.index);
      examView();
      return;
    }

    const editd = e.target.closest('[data-edit-domain]');
    if (editd) {
      modalForm('domain', state.domains.find(d => String(d.id) === String(editd.dataset.editDomain)));
      return;
    }

    const dStatus = e.target.closest('[data-domain-status]');
    if (dStatus) {
      try {
        const did = Number(dStatus.dataset.domainStatus);
        const dom = state.domains.find(d => d.id === did);
        await patch(`/api/admin/domains/${did}`, {
          ...dom,
          status: dStatus.dataset.status
        });
        await refreshAdmin();
        toast(`Domain marked as ${dStatus.dataset.status}.`);
      } catch (err) {
        toast(err.message);
      }
      return;
    }

    const dDel = e.target.closest('[data-domain-delete]');
    if (dDel) {
      if (confirm('Delete this domain permanently? It can only be deleted if no questions, students, or assessments are linked to it.')) {
        try {
          await del(`/api/admin/domains/${dDel.dataset.domainDelete}`);
          await refreshAdmin();
          toast('Domain deleted.');
        } catch (err) {
          toast(err.message);
        }
      }
      return;
    }

    const catFilter = e.target.closest('[data-filter-domain-cat]');
    if (catFilter) {
      state.filter.domainCategory = catFilter.dataset.filterDomainCat;
      renderAdmin();
      return;
    }

    const qTab = e.target.closest('[data-set-question-tab]');
    if (qTab) {
      state.questionTab = qTab.dataset.setQuestionTab;
      renderAdmin();
      return;
    }

    const addMcq = e.target.closest('[data-add-domain-mcq]');
    if (addMcq) {
      const did = Number(addMcq.dataset.addDomainMcq);
      modalForm('question', { domain_id: did, type: 'MCQ' });
      return;
    }

    const addCoding = e.target.closest('[data-add-coding-question]');
    if (addCoding) {
      const genDom = state.domains.find(d => d.name.toLowerCase() === 'general') || state.domains[0];
      modalForm('question', { domain_id: genDom?.id, type: 'Coding' });
      return;
    }

    const editq = e.target.closest('[data-edit-question]');
    if (editq) {
      modalForm('question', state.questions.find(q => q.id === editq.dataset.editQuestion));
      return;
    }

    const archq = e.target.closest('[data-archive-question]');
    if (archq) {
      const q = state.questions.find(x => x.id === archq.dataset.archiveQuestion);
      try {
        const nextStatus = q.status === 'Published' ? 'Archived' : 'Published';
        await patch(`/api/admin/questions/${encodeURIComponent(q.id)}`, {
          domainId: q.domain_id || q.domainId,
          type: q.type,
          title: q.title,
          difficulty: q.difficulty,
          status: nextStatus,
          data: q.data
        });
        await refreshAdmin();
        toast(`Question marked as ${nextStatus}.`);
      } catch (err) {
        toast(err.message);
      }
      return;
    }

    const delq = e.target.closest('[data-delete-question]');
    if (delq) {
      const qid = delq.dataset.deleteQuestion;
      const q = state.questions.find(x => x.id === qid);
      const titlePrompt = q?.title ? `"${q.title.slice(0, 45)}..."` : qid;
      if (confirm(`Are you sure you want to permanently delete question ${titlePrompt}? This action cannot be undone.`)) {
        try {
          await del(`/api/admin/questions/${encodeURIComponent(qid)}`);
          await refreshAdmin();
          toast('Question permanently deleted.');
        } catch (err) {
          toast(err.message);
        }
      }
      return;
    }

    const edits = e.target.closest('[data-edit-student]');
    if (edits) {
      modalForm('student', state.students.find(s => s.id === edits.dataset.editStudent));
      return;
    }

    const dels = e.target.closest('[data-delete-student]');
    if (dels) {
      const sid = dels.dataset.deleteStudent;
      const s = state.students.find(x => x.id === sid);
      const sName = s?.name ? `${s.name} (${sid})` : sid;
      if (confirm(`Are you sure you want to permanently delete student ${sName}? All their test attempts and submission records will also be deleted.`)) {
        try {
          await del(`/api/admin/students/${encodeURIComponent(sid)}`);
          await refreshAdmin();
          toast(`Student account ${sid} permanently deleted.`);
        } catch (err) {
          toast(err.message);
        }
      }
      return;
    }

    const edita = e.target.closest('[data-edit-assessment]');
    if (edita) {
      modalForm('assessment', state.assessments.find(a => a.id === edita.dataset.editAssessment));
      return;
    }

    const resolve = e.target.closest('[data-resolve-flag]');
    if (resolve) {
      try {
        await patch(`/api/admin/flags/${resolve.dataset.resolveFlag}`, {});
        await refreshAdmin();
        toast('Flag marked as reviewed.');
      } catch (err) {
        toast(err.message);
      }
      return;
    }

    const result = e.target.closest('[data-result]');
    if (result) {
      try {
        const data = await api(`/api/admin/results/${encodeURIComponent(result.dataset.result)}`);
        showResult(data);
      } catch (err) {
        toast(err.message);
      }
      return;
    }
  });

  document.addEventListener('change', e => {
    if (['dndCheck', 'appsCheck', 'consentCheck'].includes(e.target.id)) {
      updateStart();
    }

    if (e.target.id === 'questionDomainFilter') {
      state.filter.questionDomain = e.target.value;
      renderAdmin();
    }
    if (e.target.id === 'questionTypeFilter') {
      state.filter.questionType = e.target.value;
      renderAdmin();
    }
    if (e.target.id === 'questionDifficultyFilter') {
      state.filter.questionDifficulty = e.target.value;
      renderAdmin();
    }
    if (e.target.id === 'questionStatusFilter') {
      state.filter.questionStatus = e.target.value;
      renderAdmin();
    }
    if (e.target.id === 'studentDomainFilter') {
      state.filter.studentDomain = e.target.value;
      renderAdmin();
    }

    if (e.target.id === 'codeLanguage' && state.attempt) {
      const q = state.attempt.questions[state.index];
      const lang = e.target.value;
      q.answer = q.answer || { drafts: {} };
      q.answer.drafts = q.answer.drafts || {};
      q.answer.language = lang;
      examView();
    }

    if (e.target.id === 'bulkFile' && e.target.files?.[0]) {
      const reader = new FileReader();
      reader.onload = () => {
        const ta = $('#bulkCsvText');
        if (ta) ta.value = String(reader.result || '');
      };
      reader.readAsText(e.target.files[0]);
    }

    if (e.target.id === 'studentBulkFile' && e.target.files?.[0]) {
      const reader = new FileReader();
      reader.onload = () => {
        const ta = $('#studentCsvText');
        if (ta) ta.value = String(reader.result || '');
      };
      reader.readAsText(e.target.files[0]);
    }
  });

  document.addEventListener('input', e => {
    if (e.target.id === 'domainSearch') {
      state.search.domains = e.target.value;
      renderAdmin();
    }
    if (e.target.id === 'questionSearch') {
      state.search.questions = e.target.value;
      renderAdmin();
    }
    if (e.target.id === 'studentSearch') {
      state.search.students = e.target.value;
      renderAdmin();
    }

    if (e.target.id === 'codeAnswer' && state.attempt) {
      const q = state.attempt.questions[state.index];
      const lang = $('#codeLanguage')?.value || q.languages[0];
      q.answer = q.answer || { drafts: {} };
      q.answer.drafts = q.answer.drafts || {};
      q.answer.language = lang;
      q.answer.drafts[lang] = e.target.value;
      clearTimeout(state.saveTimer);
      state.saveTimer = setTimeout(() => saveAnswer().catch(err => toast(err.message)), 600);
    }
  });

  // PREVENT NATIVE FORM SUBMISSION: Handles AJAX submits on document level
  document.addEventListener('submit', async e => {
    if (e.target.id === 'loginForm') {
      e.preventDefault();
      const fd = new FormData(e.target);
      try {
        const data = await post('/api/auth/login', {
          loginId: fd.get('loginId'),
          password: fd.get('password')
        });
        state.user = data.user;
        state.csrf = data.csrfToken;
        resetInactivityTimer();
        if (state.user.role === 'admin') {
          state.page = 'Dashboard';
          history.pushState({ page: 'Dashboard' }, '', '/admin/dashboard');
          await refreshAdmin();
        } else {
          history.pushState({ page: '__student__' }, '', '/student/home');
          await loadStudentHome();
        }
      } catch (err) {
        loginView(err.message);
      }
      return;
    }

    if (e.target.id === 'modalForm') {
      e.preventDefault();
      clearModalError();
      try {
        await saveModal(e.target);
      } catch (err) {
        showModalError(err.message);
        toast(err.message, true);
      }
      return;
    }
  });

  function monitor(type) {
    const id = state.attempt?.attempt?.id;
    if (!id) return;
    fetch(`/api/student/attempts/${encodeURIComponent(id)}/events`, {
      method: 'POST',
      credentials: 'same-origin',
      keepalive: true,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': state.csrf
      },
      body: JSON.stringify({ type })
    })
      .then(r => r.json())
      .then(data => {
        if (type !== 'visibility') return;
        state.tabEvents = data.visibilityEvents;
        if (data.autoSubmitted) {
          clearInterval(state.timer);
          state.timer = null;
          clearCamera();
          state.attempt = null;
          if (document.fullscreenElement) {
            document.exitFullscreen().catch(() => {});
          }
          renderSubmitted('The third detected departure auto-submitted your attempt. An integrity flag was recorded.');
        } else {
          const notice = $('#eventNotice');
          if (notice) {
            notice.hidden = false;
            notice.textContent = `⚑ Warning ${state.tabEvents} of 2 · Tab departure recorded.`;
          }
        }
      })
      .catch(() => {});
  }

  document.addEventListener('visibilitychange', () => {
    if (document.hidden && state.attempt) monitor('visibility');
  });

  document.addEventListener('fullscreenchange', () => {
    if (state.attempt && !document.fullscreenElement) {
      state.fullEvents++;
      monitor('fullscreen');
      const notice = $('#eventNotice');
      if (notice) {
        notice.hidden = false;
        notice.innerHTML = '⚑ Full screen was exited. <button type="button" class="button secondary small" data-action="fullscreen">Return to full screen</button>';
      }
    }
  });

  document.addEventListener('copy', e => {
    if (state.attempt) {
      e.preventDefault();
      e.stopImmediatePropagation();
      toast('Copy and paste are disabled during this assessment.');
    }
  }, true);

  ['cut', 'paste'].forEach(type => document.addEventListener(type, e => {
    if (state.attempt) {
      e.preventDefault();
      e.stopImmediatePropagation();
      toast('Copy and paste are disabled during this assessment.');
    }
  }, true));

  document.addEventListener('selectstart', e => {
    if (state.attempt) {
      e.preventDefault();
      e.stopImmediatePropagation();
    }
  }, true);

  document.addEventListener('contextmenu', e => {
    if (state.attempt) {
      e.preventDefault();
      e.stopImmediatePropagation();
    }
  }, true);

  document.addEventListener('keydown', e => {
    if (!state.attempt) return;
    const key = e.key.toLowerCase();
    const mod = e.ctrlKey || e.metaKey;
    if ((mod && ['a', 'c', 'v', 'x'].includes(key)) || (e.shiftKey && ['insert', 'delete'].includes(key)) || (e.shiftKey && key.startsWith('arrow'))) {
      e.preventDefault();
      e.stopImmediatePropagation();
      if (key !== 'a') toast('Copy and paste are disabled during this assessment.');
    }
  }, true);

  modal.addEventListener('click', e => {
    if (e.target === modal) modal.close();
  });

  modal.addEventListener('close', () => {
    clearModalError();
    modal.classList.remove('confirm-modal');
    modal.classList.remove('wide');
    if (toastNode && toastNode.parentElement !== document.body) {
      document.body.appendChild(toastNode);
    }
  });

  // Password visibility toggle (reveals for 2 seconds then hides automatically)
  document.addEventListener('click', e => {
    const btn = e.target.closest('.password-toggle-btn');
    if (!btn) return;
    e.preventDefault();
    const wrap = btn.closest('.password-input-wrap') || btn.parentElement;
    const input = wrap?.querySelector('input');
    if (!input) return;

    clearTimeout(btn._hideTimer);
    if (input.type === 'text') {
      input.type = 'password';
      btn.classList.remove('active');
      btn.innerHTML = EYE_ICON_SVG;
      btn.setAttribute('aria-label', 'Show password (2s preview)');
      btn.setAttribute('title', 'Show password for 2 seconds');
    } else {
      input.type = 'text';
      btn.classList.add('active');
      btn.innerHTML = EYE_OFF_ICON_SVG;
      btn.setAttribute('aria-label', 'Hide password');
      btn.setAttribute('title', 'Click to hide now');
      btn._hideTimer = setTimeout(() => {
        input.type = 'password';
        btn.classList.remove('active');
        btn.innerHTML = EYE_ICON_SVG;
        btn.setAttribute('aria-label', 'Show password (2s preview)');
        btn.setAttribute('title', 'Show password for 2 seconds');
      }, 2000);
    }
  });

  // App Initialization
  (async () => {
    try {
      const pathname = window.location.pathname.replace(/\/$/, '') || '/admin/dashboard';
      if (pathname === '/login' || pathname === '/admin/login') {
        try { await post('/api/auth/logout', {}); } catch (_) {}
        state.user = null;
        state.csrf = '';
        return loginView();
      }

      const data = await api('/api/auth/me');
      state.user = data.user;
      state.csrf = data.csrfToken || '';
      if (!state.user) return loginView();
      resetInactivityTimer();
      if (state.user.role === 'admin') {
        // Parse the current URL to decide which admin page to open
        const routedPage = PAGE_ROUTES[pathname];
        if (routedPage && routedPage !== '__student__' && routedPage !== '__login__') {
          state.page = routedPage;
        }
        // Ensure a valid history entry for the current page
        const canonicalPath = PAGE_PATHS[state.page] || '/admin/dashboard';
        if (window.location.pathname !== canonicalPath) {
          history.replaceState({ page: state.page }, '', canonicalPath);
        }
        await refreshAdmin();
      } else {
        await loadStudentHome();
      }
    } catch (e) {
      loginView(e.message);
    }
  })();
})();
