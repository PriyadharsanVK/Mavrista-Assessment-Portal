# Assessment Portal

A secure, production-grade assessment platform designed for evaluating technical skills across Software and Electronics domains. Built entirely with the Python standard library on the backend and modern vanilla JavaScript & CSS on the frontend. No external dependencies, heavy frameworks, or node_modules are required.

---

## 🌟 Key Features

- **Domain-Driven Evaluations**: Supports **Software** and **Electrical / Electronics** domains.
- **Custom Question Quotas**:
  - **Standard / Software Domains**: 25 MCQs + 2 Coding Challenges (60-minute duration).
  - **8 Dedicated Electronics Domains**: 30 MCQs + 0 Coding (60-minute duration):
    - *Arduino & Microcontroller*
    - *Digital Electronics*
    - *Electronic Product Design*
    - *Electronics Circuit*
    - *Electronics Quality*
    - *IOT Hardware Development*
    - *PCB Design Development*
    - *VLSI Design*
- **IST Fixed Scheduling**: All assessment windows and timers are synchronized in India Standard Time (IST, UTC+5:30).
- **Isolated Code Runner**: Sandboxed Docker runner for Python, JavaScript, Java, C++, and C with no network access, memory limits, process quotas, and strict timeouts.
- **Anti-Cheating & Integrity Guard**:
  - Fullscreen departure detection and tab departure warnings.
  - Automatic test submission on repeated integrity breaches.
  - Page-level clipboard restrictions (copy, cut, paste disabled).
  - Live proctoring camera preview (privacy-first: video stays local to the client).
- **Two-Way Google Sheets Sync**: Real-time sync of domains, questions, students, assessments, and test results with Google Sheets.
- **Automated Task Submission Integration**: Automatically enrolls students from internship task submission forms, schedules their assessment for **2 days later at 6:00 PM IST**, and emails them their credentials.
- **Storage Auto-Cleanup**: Daily background purge of completed/expired sessions and attempts older than the configurable retention window (default 90 days), preventing disk exhaustion while permanent archives live in Google Sheets.

---

## 📁 Project Structure

```text
├── index.html          # Clean SPA shell with Content-Security-Policy & DM Sans typography
├── styles.css          # Modern design system (rich emerald/slate palette, responsive)
├── app.js              # Single-page application logic, student proctoring, & admin UI
├── server.py           # Multi-threaded Python HTTP server, SQLite WAL backend, REST API
├── create_admin.py     # Secure CLI utility to bootstrap admin credentials
├── runner/             # Isolated Docker execution container configuration
│   ├── Dockerfile
│   └── runner.py
├── tests/              # Unit and integration test suite
│   └── test_api.py
├── .gitignore          # Production git ignore (protects databases, logs, virtualenvs)
└── README.md           # Documentation
```

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+ (Standard library only; zero `pip install` required)
- Docker (optional, only required if executing student coding challenges locally)

### 2. Create the First Admin Account
```bash
python create_admin.py
```
Follow the interactive prompts to set your Admin Name, Email, and a secure password (12+ characters).

### 3. Launch the Server
```bash
python server.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```
Sign in with your newly created admin credentials.

---

## ⚡ Seed Sample Data (Optional)
To test the portal with pre-populated domains, sample questions, and a demo student (`ST-DEMO`):

**PowerShell (Windows):**
```powershell
$env:ASSESSMENT_SEED_SAMPLE = "1"
$env:ASSESSMENT_DEMO_PASSWORD = "DemoPassword@2026"
python server.py
```

**Bash (Linux / macOS):**
```bash
ASSESSMENT_SEED_SAMPLE=1 ASSESSMENT_DEMO_PASSWORD="DemoPassword@2026" python3 server.py
```

---

## 📊 Google Sheets Live Sync Integration

The portal integrates with Google Sheets via a Google Apps Script Web App for two-way synchronization:

1. Create a Google Sheet (e.g. *Assessment Portal Master*).
2. Go to **Extensions > Apps Script**.
3. Create a script with the following `doPost(e)` sync handler:

```javascript
function doPost(e) {
  try {
    var payload = JSON.parse(e.postData.contents || '{}');
    var action = payload.action;
    var ss = SpreadsheetApp.getActiveSpreadsheet();

    if (action === 'read_all') {
      return ContentService.createTextOutput(JSON.stringify(readAllData(ss)))
        .setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'append') {
      var sheet = getOrCreateSheet(ss, payload.sheet || 'Data');
      appendRowData(sheet, payload.sheet, payload.data || {});
      return ContentService.createTextOutput(JSON.stringify({ ok: true }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    if (action === 'sync_all') {
      syncMasterData(ss, payload.data || {});
      return ContentService.createTextOutput(JSON.stringify({ ok: true }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(JSON.stringify({ error: 'Unknown action' }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function getOrCreateSheet(ss, name) {
  var sheet = ss.getSheetByName(name);
  return sheet ? sheet : ss.insertSheet(name);
}
```
4. Deploy the script: **Deploy > New deployment > Web app**:
   - **Execute as**: `Me`
   - **Who has access**: `Anyone`
5. In the Assessment Portal, click **Sheets Sync** in the top navigation bar, paste your Web App URL, and click **Save & Sync All**.

---

## 🤖 Internship Task Submission Automation

When interns submit their task form in Google Forms, they select their package (e.g., *Certificate + Assessment*). 

To connect an existing Task Submission Google Sheet **without breaking any existing scripts**:

### 1. Add `AssessmentEnrollment.gs` to Apps Script
1. In your Task Submission Google Sheet, click **Extensions > Apps Script**.
2. Click the **`+`** icon beside Files > select **Script** > name it `AssessmentEnrollment.gs`.
3. Paste the following complete, self-contained handler:

```javascript
/**
 * MAVRISTA TECHNOLOGIES — ASSESSMENT PORTAL
 * AssessmentEnrollment.gs — Automated Student & Assessment Provisioning
 *
 * RULES:
 * - 8 Electronics Domains: 30 MCQs, 0 Coding (60 minutes).
 * - All Other Domains: 25 MCQs, 2 Coding challenges (60 minutes).
 * - Schedule: Registration Date + 2 Days @ 18:00:00 (6:00 PM IST).
 * - Anti-Duplicate: Never re-emails or duplicates an already scheduled student.
 */

var ASSESSMENT_CONFIG = {
  PORTAL_URL: "https://assessment.mavrista.com", // Replace with your portal URL
  PORTAL_API_URL: "", // Optional webhook endpoint
  BANNER_URL: "https://www.mavrista.com/images/email-banner.png",
  COMPANY_NAME: "Mavrista Technologies",
  SUPPORT_EMAIL: "support@mavrista.com",
  TIME_ZONE: "Asia/Kolkata",
  
  STATUS_HEADER: "Assessment Status",
  SCHEDULED_TIME_HEADER: "Assessment Scheduled For",
  EMAIL_SENT_HEADER: "Assessment Credentials Sent At"
};

var ELECTRONICS_DOMAINS = [
  "arduino & microcontroller",
  "arduino_&_microcontroller",
  "digital electronics",
  "digital_electronics",
  "electronic product design",
  "electronic_product_design",
  "electronics circuit",
  "electronics_circuit",
  "electronics quality",
  "electronics_quality",
  "iot hardware development",
  "iot_hardware_development",
  "pcb design development",
  "pcb_design_development",
  "vlsi design",
  "vlsi_design"
];

function handleAssessmentEnrollment(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (lockErr) {
    console.warn("Could not obtain lock for assessment enrollment: " + lockErr.message);
  }

  try {
    var sheet = e && e.range ? e.range.getSheet() : SpreadsheetApp.getActiveSheet();
    var rowNumber = e && e.range ? e.range.getRow() : sheet.getActiveCell().getRow();

    if (rowNumber < 2) return;

    ensureAssessmentTrackingColumns_(sheet);
    var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0].map(function(h) {
      return String(h || "").trim();
    });

    var currentStatus = String(getCellValueByHeader_(sheet, headers, rowNumber, ASSESSMENT_CONFIG.STATUS_HEADER) || "").trim();
    if (currentStatus.indexOf("SCHEDULED") !== -1 || currentStatus.indexOf("NOT_REQUESTED") !== -1) {
      console.log("Row " + rowNumber + " already has Assessment Status: " + currentStatus + ". Skipping.");
      return;
    }

    var rowValues = sheet.getRange(rowNumber, 1, 1, sheet.getLastColumn()).getValues()[0];

    var packageValues = [];
    headers.forEach(function(h, idx) {
      if (h.toLowerCase().indexOf("select your package") !== -1) {
        var val = String(rowValues[idx] || "").trim();
        if (val) packageValues.push(val);
      }
    });

    var requestedAssessment = packageValues.some(function(pkg) {
      return pkg.toLowerCase().indexOf("assessment") !== -1;
    });

    if (!requestedAssessment) {
      setCellValueByHeader_(sheet, headers, rowNumber, ASSESSMENT_CONFIG.STATUS_HEADER, "NOT_REQUESTED");
      SpreadsheetApp.flush();
      return;
    }

    var firstName = getCellValueByHeader_(sheet, headers, rowNumber, "First Name");
    var lastName = getCellValueByHeader_(sheet, headers, rowNumber, "Last Name");
    var fullName = (firstName + " " + lastName).trim() || "Student";
    
    var email = getCellValueByHeader_(sheet, headers, rowNumber, "Registered Mail ID") ||
                getCellValueByHeader_(sheet, headers, rowNumber, "Email Address");
    
    var studentId = getCellValueByHeader_(sheet, headers, rowNumber, "Registration/Application ID") ||
                    ("ST-" + new Date().getTime());
    
    var domain = getCellValueByHeader_(sheet, headers, rowNumber, "Internship Domain") || "General";
    
    var rawTimestamp = getCellValueByHeader_(sheet, headers, rowNumber, "Timestamp");
    var baseDate = rawTimestamp ? new Date(rawTimestamp) : new Date();
    if (isNaN(baseDate.getTime())) baseDate = new Date();

    if (!email) {
      setCellValueByHeader_(sheet, headers, rowNumber, ASSESSMENT_CONFIG.STATUS_HEADER, "ERROR_MISSING_EMAIL");
      return;
    }

    var scheduledDate = new Date(baseDate.getTime());
    scheduledDate.setDate(scheduledDate.getDate() + 2);
    scheduledDate.setHours(18, 0, 0, 0);

    var formattedDate = Utilities.formatDate(scheduledDate, ASSESSMENT_CONFIG.TIME_ZONE, "EEEE, dd MMMM yyyy 'at' hh:mm a 'IST'");

    var isElectronics = isElectronicsDomain_(domain);
    var mcqCount = isElectronics ? 30 : 25;
    var codingCount = isElectronics ? 0 : 2;
    var testStructure = isElectronics 
      ? "30 Multiple Choice Questions (Theory / Analysis)" 
      : "25 Multiple Choice Questions + 2 Coding Challenges";

    var initialPassword = studentId + "@2026";

    sendAssessmentScheduleEmail_({
      email: email,
      fullName: fullName,
      studentId: studentId,
      password: initialPassword,
      domain: domain,
      formattedDate: formattedDate,
      duration: "60 Minutes",
      testStructure: testStructure,
      portalUrl: ASSESSMENT_CONFIG.PORTAL_URL
    });

    setCellValueByHeader_(sheet, headers, rowNumber, ASSESSMENT_CONFIG.STATUS_HEADER, "SCHEDULED (" + studentId + ")");
    setCellValueByHeader_(sheet, headers, rowNumber, ASSESSMENT_CONFIG.SCHEDULED_TIME_HEADER, formattedDate);
    setCellValueByHeader_(sheet, headers, rowNumber, ASSESSMENT_CONFIG.EMAIL_SENT_HEADER, new Date());
    SpreadsheetApp.flush();

    console.log("Successfully scheduled assessment for: " + studentId + " (" + email + ")");

  } catch (err) {
    console.error("handleAssessmentEnrollment error: " + err.message);
  } finally {
    try { lock.releaseLock(); } catch (_) {}
  }
}

function sendAssessmentScheduleEmail_(data) {
  var safeName = escapeHtml_(data.fullName);
  var safeId = escapeHtml_(data.studentId);
  var safePassword = escapeHtml_(data.password);
  var safeDomain = escapeHtml_(data.domain);
  var safeDate = escapeHtml_(data.formattedDate);
  var safeDuration = escapeHtml_(data.duration);
  var safeStructure = escapeHtml_(data.testStructure);
  var safePortalUrl = escapeHtml_(data.portalUrl);

  var htmlBody = `
    <div style="font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;max-width:620px;margin:auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;color:#1e293b;line-height:1.6">
      <img src="${ASSESSMENT_CONFIG.BANNER_URL}" alt="Mavrista Technologies" style="width:100%;max-width:620px;height:auto;display:block;border-bottom:1px solid #e2e8f0" onerror="this.style.display='none'">
      
      <div style="padding:28px 24px">
        <h2 style="color:#0f3a2f;margin-top:0;font-size:22px;letter-spacing:-0.4px">🎯 Your Assessment has been Scheduled</h2>
        <p>Dear <b>${safeName}</b>,</p>
        <p>Thank you for submitting your internship task. Based on your package selection, your technical assessment has been scheduled. Please find your schedule and sign-in credentials below:</p>

        <div style="background:#f0f7f3;border:1px solid #cfe5d7;border-radius:10px;padding:18px 20px;margin:22px 0">
          <table style="width:100%;border-collapse:collapse;font-size:14px">
            <tr>
              <td style="padding:6px 0;color:#526d63;width:150px"><b>Internship Domain:</b></td>
              <td style="padding:6px 0;color:#0f3a2f"><b>${safeDomain}</b></td>
            </tr>
            <tr>
              <td style="padding:6px 0;color:#526d63"><b>Date & Time (IST):</b></td>
              <td style="padding:6px 0;color:#0f3a2f"><b>${safeDate}</b></td>
            </tr>
            <tr>
              <td style="padding:6px 0;color:#526d63"><b>Duration:</b></td>
              <td style="padding:6px 0;color:#0f3a2f">${safeDuration}</td>
            </tr>
            <tr>
              <td style="padding:6px 0;color:#526d63"><b>Format:</b></td>
              <td style="padding:6px 0;color:#0f3a2f">${safeStructure}</td>
            </tr>
          </table>
        </div>

        <div style="background:#ffffff;border:1px dashed #28785e;border-radius:10px;padding:16px 20px;margin:20px 0">
          <p style="margin:0 0 8px 0;font-size:12px;color:#28785e;text-transform:uppercase;font-weight:700;letter-spacing:1px">Your Assessment Login Credentials</p>
          <table style="width:100%;border-collapse:collapse;font-size:14px">
            <tr>
              <td style="padding:4px 0;color:#64748b;width:140px">Portal URL:</td>
              <td style="padding:4px 0"><a href="${safePortalUrl}" target="_blank" style="color:#185e4b;font-weight:600">${safePortalUrl}</a></td>
            </tr>
            <tr>
              <td style="padding:4px 0;color:#64748b">Student ID / Login:</td>
              <td style="padding:4px 0"><code style="background:#f1f5f9;padding:3px 8px;border-radius:5px;font-size:13px;font-weight:700;color:#0f172a">${safeId}</code></td>
            </tr>
            <tr>
              <td style="padding:4px 0;color:#64748b">Temporary Password:</td>
              <td style="padding:4px 0"><code style="background:#f1f5f9;padding:3px 8px;border-radius:5px;font-size:13px;font-weight:700;color:#0f172a">${safePassword}</code></td>
            </tr>
          </table>
        </div>

        <div style="text-align:center;margin:28px 0">
          <a href="${safePortalUrl}" target="_blank" style="background:#185e4b;color:#ffffff;text-decoration:none;padding:13px 32px;border-radius:8px;font-weight:700;font-size:14px;display:inline-block;box-shadow:0 4px 12px rgba(24,94,75,0.25)">
            Open Assessment Portal ➔
          </a>
        </div>

        <div style="border-top:1px solid #e2e8f0;padding-top:16px;margin-top:22px;font-size:12px;color:#64748b">
          <strong style="color:#334155;display:block;margin-bottom:6px">📌 Mandatory Assessment Guidelines:</strong>
          <ul style="margin:0;padding-left:18px;line-height:1.7">
            <li>The assessment starts strictly at <b>6:00 PM IST</b> on the scheduled date.</li>
            <li>Use a desktop or laptop computer with the latest Google Chrome browser. Mobile phones and tablets are not supported.</li>
            <li>Webcam permission is required throughout the assessment.</li>
            <li>Tab switching and exiting fullscreen mode are actively tracked and will lead to automatic submission.</li>
          </ul>
        </div>

        <p style="margin-top:24px;font-size:13px;color:#475569">
          Best regards,<br>
          <b>Mavrista Technologies Evaluation Team</b><br>
          <a href="mailto:${ASSESSMENT_CONFIG.SUPPORT_EMAIL}" style="color:#185e4b">${ASSESSMENT_CONFIG.SUPPORT_EMAIL}</a>
        </p>
      </div>
    </div>
  `;

  MailApp.sendEmail({
    to: data.email,
    subject: "Mavrista Technologies | Assessment Scheduled (" + data.domain + ")",
    htmlBody: htmlBody
  });
}

function isElectronicsDomain_(domainName) {
  var normalized = String(domainName || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");

  return ELECTRONICS_DOMAINS.some(function(item) {
    var check = item.toLowerCase().replace(/\s+/g, "_");
    return normalized.indexOf(check) !== -1 || check.indexOf(normalized) !== -1;
  });
}

function ensureAssessmentTrackingColumns_(sheet) {
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0].map(function(h) {
    return String(h || "").trim();
  });

  [
    ASSESSMENT_CONFIG.STATUS_HEADER,
    ASSESSMENT_CONFIG.SCHEDULED_TIME_HEADER,
    ASSESSMENT_CONFIG.EMAIL_SENT_HEADER
  ].forEach(function(header) {
    if (headers.indexOf(header) === -1) {
      sheet.getRange(1, sheet.getLastColumn() + 1).setValue(header);
      headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0].map(function(h) {
        return String(h || "").trim();
      });
    }
  });
}

function getCellValueByHeader_(sheet, headers, rowNumber, headerName) {
  var index = headers.indexOf(headerName);
  if (index === -1) return "";
  return sheet.getRange(rowNumber, index + 1).getValue();
}

function setCellValueByHeader_(sheet, headers, rowNumber, headerName, value) {
  var index = headers.indexOf(headerName);
  if (index === -1) {
    ensureAssessmentTrackingColumns_(sheet);
    headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0].map(function(h) {
      return String(h || "").trim();
    });
    index = headers.indexOf(headerName);
  }
  if (index !== -1) {
    sheet.getRange(rowNumber, index + 1).setValue(value);
  }
}

function escapeHtml_(text) {
  return String(text == null ? "" : text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function enrollPendingAssessmentsManually() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    Logger.log("No data rows found.");
    return;
  }

  ensureAssessmentTrackingColumns_(sheet);
  Logger.log("Scanning " + (lastRow - 1) + " rows for pending assessment requests...");

  for (var r = 2; r <= lastRow; r++) {
    handleAssessmentEnrollment({
      range: sheet.getRange(r, 1)
    });
  }

  Logger.log("Manual scan complete.");
}
```

### 2. Connect to `onFormSubmit`
In your existing `PaymentAutomation.gs`, inside `onFormSubmit(e)`, add these lines right after the payment link is sent:

```javascript
    // Automatically schedule assessment & email credentials if assessment package selected
    try {
      handleAssessmentEnrollment(e);
    } catch (enrollError) {
      console.warn("Assessment enrollment notice: " + (enrollError && enrollError.message ? enrollError.message : enrollError));
    }
```

---

## 🐳 Isolated Coding Execution Runner

To execute student code submissions in an isolated environment:
1. Ensure Docker is installed and running.
2. Build the runner container image:
   ```bash
   docker build -t assessment-runner:local runner
   ```
3. The runner executes code in an unprivileged, read-only scratch space with network access permanently disabled.

---

## 🔒 Security Best Practices

- **Production Deployment**: Host behind an HTTPS reverse proxy (e.g. Caddy, Nginx).
- **Secure Cookies**: Set `ASSESSMENT_COOKIE_SECURE=1` when serving over HTTPS.
- **CSRF & Sessions**: All mutations require anti-CSRF token verification and SameSite strict cookies.
- **Content-Security-Policy**: Configured with strict `default-src 'self'`, forbidding untrusted origins or inline frames.

---

## 🧪 Testing

Run the automated unittest suite:
```bash
python -m unittest discover tests -v
```
The test suite validates authentication, role authorization, pool drawing, integrity warnings, autosaving, scoring, and sheet synchronization.
