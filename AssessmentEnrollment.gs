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

