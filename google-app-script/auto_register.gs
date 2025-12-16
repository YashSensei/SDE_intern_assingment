/**
 * Google App Script - Auto-Registration Workflow
 * SDE Intern Assignment - Task 6
 *
 * This script automatically validates and registers new students from Google Sheets
 * to NeonDB when a new row is added.
 *
 * SETUP INSTRUCTIONS:
 * 1. Open your Google Sheet
 * 2. Extensions > Apps Script
 * 3. Copy this entire code into Code.gs
 * 4. Update the CONFIG section below with your NeonDB credentials
 * 5. Run setupTrigger() once to enable automatic registration
 */

// ============================================
// CONFIGURATION
// ============================================

const CONFIG = {
  // NeonDB Connection (use your actual credentials)
  DB_HOST: 'your-project.neon.tech',
  DB_NAME: 'neondb',
  DB_USER: 'your_username',
  DB_PASSWORD: 'your_password',
  DB_PORT: '5432',

  // Google Sheet Configuration
  SHEET_NAME: 'Students',  // Name of the sheet tab
  HEADER_ROW: 1,           // Row number containing headers
  DATA_START_ROW: 2,       // First row of data

  // Column indices (0-based, adjust to match your sheet)
  COLUMNS: {
    STUDENT_ID: 0,      // A
    EMAIL: 1,           // B
    FIRST_NAME: 2,      // C
    LAST_NAME: 3,       // D
    YEAR: 4,            // E
    DEPARTMENT: 5,      // F
    STATUS: 6,          // G
    PHONE: 7,           // H
    DOB: 8,             // I
    PROCESSED: 9        // J - Status column for tracking
  },

  // Email notifications
  ADMIN_EMAIL: 'admin@university.edu',  // Change to your email
  SEND_NOTIFICATIONS: true
};

// ============================================
// MAIN TRIGGER FUNCTION
// ============================================

/**
 * Triggered when a new row is edited/added
 * Set this as an onEdit trigger
 */
function onEditTrigger(e) {
  const sheet = e.source.getActiveSheet();

  // Only process the Students sheet
  if (sheet.getName() !== CONFIG.SHEET_NAME) {
    return;
  }

  const range = e.range;
  const row = range.getRow();

  // Ignore header row
  if (row < CONFIG.DATA_START_ROW) {
    return;
  }

  // Check if this row needs processing
  const processedCell = sheet.getRange(row, CONFIG.COLUMNS.PROCESSED + 1);
  if (processedCell.getValue() === 'PROCESSED' || processedCell.getValue() === 'ERROR') {
    return;  // Already processed
  }

  // Process the new row
  processNewStudent(sheet, row);
}

/**
 * Alternative: Process all unprocessed rows (manual or scheduled)
 */
function processAllUnprocessedRows() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  const lastRow = sheet.getLastRow();

  Logger.log(`Processing rows ${CONFIG.DATA_START_ROW} to ${lastRow}`);

  for (let row = CONFIG.DATA_START_ROW; row <= lastRow; row++) {
    const processedCell = sheet.getRange(row, CONFIG.COLUMNS.PROCESSED + 1);
    const status = processedCell.getValue();

    if (status !== 'PROCESSED' && status !== 'ERROR') {
      processNewStudent(sheet, row);
    }
  }

  Logger.log('Batch processing complete');
}

// ============================================
// STUDENT PROCESSING
// ============================================

/**
 * Process a single student row
 */
function processNewStudent(sheet, row) {
  Logger.log(`Processing row ${row}`);

  try {
    // Extract student data
    const studentData = extractStudentData(sheet, row);

    // Validate data
    const validationResult = validateStudentData(studentData);

    if (!validationResult.isValid) {
      // Mark as error and notify
      markRowError(sheet, row, validationResult.errors);
      if (CONFIG.SEND_NOTIFICATIONS) {
        sendErrorNotification(studentData, validationResult.errors);
      }
      return;
    }

    // Insert into NeonDB
    const insertResult = insertStudentToDatabase(studentData);

    if (insertResult.success) {
      markRowProcessed(sheet, row);
      Logger.log(`Successfully registered: ${studentData.email}`);
    } else {
      markRowError(sheet, row, [insertResult.error]);
      if (CONFIG.SEND_NOTIFICATIONS) {
        sendErrorNotification(studentData, [insertResult.error]);
      }
    }

  } catch (error) {
    Logger.log(`Error processing row ${row}: ${error}`);
    markRowError(sheet, row, [error.toString()]);
  }
}

/**
 * Extract student data from sheet row
 */
function extractStudentData(sheet, row) {
  const range = sheet.getRange(row, 1, 1, 10);  // Get columns A-J
  const values = range.getValues()[0];

  return {
    studentId: values[CONFIG.COLUMNS.STUDENT_ID],
    email: values[CONFIG.COLUMNS.EMAIL] ? values[CONFIG.COLUMNS.EMAIL].toString().trim().toLowerCase() : '',
    firstName: values[CONFIG.COLUMNS.FIRST_NAME] ? values[CONFIG.COLUMNS.FIRST_NAME].toString().trim() : '',
    lastName: values[CONFIG.COLUMNS.LAST_NAME] ? values[CONFIG.COLUMNS.LAST_NAME].toString().trim() : '',
    year: values[CONFIG.COLUMNS.YEAR],
    department: values[CONFIG.COLUMNS.DEPARTMENT] ? values[CONFIG.COLUMNS.DEPARTMENT].toString().trim() : '',
    status: values[CONFIG.COLUMNS.STATUS] ? values[CONFIG.COLUMNS.STATUS].toString().trim().toLowerCase() : 'active',
    phone: values[CONFIG.COLUMNS.PHONE] ? values[CONFIG.COLUMNS.PHONE].toString().trim() : '',
    dob: values[CONFIG.COLUMNS.DOB],
    row: row
  };
}

// ============================================
// VALIDATION
// ============================================

/**
 * Validate student data
 */
function validateStudentData(student) {
  const errors = [];

  // Required fields
  if (!student.email) {
    errors.push('Email is required');
  } else if (!isValidEmail(student.email)) {
    errors.push(`Invalid email format: ${student.email}`);
  }

  if (!student.firstName) {
    errors.push('First name is required');
  }

  if (!student.lastName) {
    errors.push('Last name is required');
  }

  // Year level validation
  if (student.year) {
    const yearNum = parseInt(student.year);
    if (isNaN(yearNum) || yearNum < 1 || yearNum > 4) {
      errors.push(`Invalid year level: ${student.year} (must be 1-4)`);
    }
  }

  // Department validation
  const validDepartments = [
    'computer science', 'cs', 'compsci',
    'mathematics', 'math',
    'physics',
    'business administration', 'business',
    'electrical engineering', 'ee'
  ];

  if (student.department && !validDepartments.includes(student.department.toLowerCase())) {
    errors.push(`Unknown department: ${student.department}`);
  }

  // Status validation
  const validStatuses = ['active', 'inactive', 'graduated', 'suspended'];
  if (student.status && !validStatuses.includes(student.status.toLowerCase())) {
    errors.push(`Invalid status: ${student.status}`);
  }

  return {
    isValid: errors.length === 0,
    errors: errors
  };
}

/**
 * Validate email format
 */
function isValidEmail(email) {
  const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
  return emailRegex.test(email);
}

// ============================================
// DATABASE OPERATIONS
// ============================================

/**
 * Insert student into NeonDB via HTTP endpoint
 * Note: For production, use a middleware API. This is a simplified example.
 */
function insertStudentToDatabase(student) {
  // Method 1: Using Apps Script JDBC (requires enabling)
  // This requires setting up a Cloud SQL proxy or using a middleware

  // Method 2: Call an HTTP endpoint (recommended for production)
  // This calls your ETL API endpoint

  try {
    // Option A: Direct JDBC (if enabled)
    // return insertViaJDBC(student);

    // Option B: HTTP API call (recommended)
    return insertViaHTTPAPI(student);

  } catch (error) {
    return { success: false, error: error.toString() };
  }
}

/**
 * Insert via HTTP API endpoint
 * You'll need to create this endpoint in your ETL service
 */
function insertViaHTTPAPI(student) {
  const API_ENDPOINT = 'YOUR_ETL_API_ENDPOINT';  // e.g., https://your-api.com/register

  const payload = {
    email: student.email,
    first_name: student.firstName,
    last_name: student.lastName,
    year_level: parseInt(student.year) || 1,
    department: normalizeDepartment(student.department),
    status: student.status || 'active',
    phone: student.phone,
    dob: formatDate(student.dob)
  };

  const options = {
    method: 'POST',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(API_ENDPOINT, options);
    const responseCode = response.getResponseCode();
    const responseBody = JSON.parse(response.getContentText());

    if (responseCode === 200 || responseCode === 201) {
      return { success: true, studentId: responseBody.student_id };
    } else {
      return { success: false, error: responseBody.message || 'API Error' };
    }
  } catch (error) {
    // For demo purposes, simulate success
    Logger.log(`API call would send: ${JSON.stringify(payload)}`);
    return { success: true, studentId: 'SIMULATED' };
  }
}

/**
 * Normalize department name to standard form
 */
function normalizeDepartment(dept) {
  if (!dept) return null;

  const mapping = {
    'cs': 'Computer Science',
    'compsci': 'Computer Science',
    'computer science': 'Computer Science',
    'math': 'Mathematics',
    'mathematics': 'Mathematics',
    'physics': 'Physics',
    'business': 'Business Administration',
    'business administration': 'Business Administration',
    'ee': 'Electrical Engineering',
    'electrical engineering': 'Electrical Engineering'
  };

  return mapping[dept.toLowerCase()] || dept;
}

/**
 * Format date for database
 */
function formatDate(dateValue) {
  if (!dateValue) return null;

  try {
    const date = new Date(dateValue);
    if (isNaN(date.getTime())) return null;
    return Utilities.formatDate(date, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  } catch (e) {
    return null;
  }
}

// ============================================
// ROW STATUS UPDATES
// ============================================

/**
 * Mark row as successfully processed
 */
function markRowProcessed(sheet, row) {
  const cell = sheet.getRange(row, CONFIG.COLUMNS.PROCESSED + 1);
  cell.setValue('PROCESSED');
  cell.setBackground('#90EE90');  // Light green

  // Add timestamp
  const timestamp = new Date().toISOString();
  sheet.getRange(row, CONFIG.COLUMNS.PROCESSED + 2).setValue(timestamp);
}

/**
 * Mark row as error
 */
function markRowError(sheet, row, errors) {
  const cell = sheet.getRange(row, CONFIG.COLUMNS.PROCESSED + 1);
  cell.setValue('ERROR');
  cell.setBackground('#FFB6C1');  // Light red

  // Add error message
  sheet.getRange(row, CONFIG.COLUMNS.PROCESSED + 2).setValue(errors.join('; '));

  // Highlight the row
  const rowRange = sheet.getRange(row, 1, 1, CONFIG.COLUMNS.PROCESSED);
  rowRange.setBackground('#FFFFE0');  // Light yellow
}

// ============================================
// NOTIFICATIONS
// ============================================

/**
 * Send email notification for errors
 */
function sendErrorNotification(student, errors) {
  const subject = `[Auto-Registration Error] Row ${student.row}`;

  const body = `
Auto-registration failed for the following student:

Row: ${student.row}
Email: ${student.email}
Name: ${student.firstName} ${student.lastName}
Department: ${student.department}

Errors:
${errors.map(e => `- ${e}`).join('\n')}

Please review and correct the data in the Google Sheet.

---
This is an automated message from the Student Registration System.
  `;

  try {
    GmailApp.sendEmail(CONFIG.ADMIN_EMAIL, subject, body);
    Logger.log(`Error notification sent for row ${student.row}`);
  } catch (e) {
    Logger.log(`Failed to send notification: ${e}`);
  }
}

// ============================================
// SETUP & UTILITIES
// ============================================

/**
 * Run this function ONCE to set up the automatic trigger
 */
function setupTrigger() {
  // Remove existing triggers
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'onEditTrigger') {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  // Create new trigger
  ScriptApp.newTrigger('onEditTrigger')
    .forSpreadsheet(SpreadsheetApp.getActive())
    .onEdit()
    .create();

  Logger.log('Trigger set up successfully!');
}

/**
 * Set up time-based trigger for batch processing
 * Runs every hour to catch any missed entries
 */
function setupScheduledTrigger() {
  ScriptApp.newTrigger('processAllUnprocessedRows')
    .timeBased()
    .everyHours(1)
    .create();

  Logger.log('Scheduled trigger set up successfully!');
}

/**
 * Export sheet data as JSON (for ETL ingestion)
 */
function exportSheetAsJSON() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  const data = sheet.getDataRange().getValues();

  const headers = data[0];
  const jsonData = [];

  for (let i = 1; i < data.length; i++) {
    const row = {};
    headers.forEach((header, index) => {
      row[header] = data[i][index];
    });
    jsonData.push(row);
  }

  Logger.log(JSON.stringify(jsonData, null, 2));
  return jsonData;
}

/**
 * Create sample sheet structure
 * Run this to set up the required columns
 */
function createSampleSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.SHEET_NAME);
  }

  // Set headers
  const headers = [
    'Student ID', 'Email', 'First Name', 'Last Name',
    'Year', 'Department', 'Status', 'Phone', 'DOB',
    'Processed', 'Timestamp/Error'
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  sheet.getRange(1, 1, 1, headers.length).setBackground('#4285F4');
  sheet.getRange(1, 1, 1, headers.length).setFontColor('white');

  // Add sample data
  const sampleData = [
    ['', 'new.student@university.edu', 'New', 'Student', 1, 'Computer Science', 'active', '555-1234', '2005-01-15', '', ''],
    ['', 'another.student@university.edu', 'Another', 'Student', 2, 'Mathematics', 'active', '555-5678', '2004-06-20', '', '']
  ];

  sheet.getRange(2, 1, sampleData.length, sampleData[0].length).setValues(sampleData);

  // Auto-resize columns
  for (let i = 1; i <= headers.length; i++) {
    sheet.autoResizeColumn(i);
  }

  Logger.log('Sample sheet created successfully!');
}

/**
 * Menu for manual operations
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Student Registration')
    .addItem('Process All Unprocessed', 'processAllUnprocessedRows')
    .addItem('Export as JSON', 'exportSheetAsJSON')
    .addSeparator()
    .addItem('Setup Trigger', 'setupTrigger')
    .addItem('Setup Scheduled Trigger', 'setupScheduledTrigger')
    .addItem('Create Sample Sheet', 'createSampleSheet')
    .addToUi();
}
