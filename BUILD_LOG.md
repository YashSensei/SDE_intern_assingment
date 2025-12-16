# SDE Intern Assignment - Build Log

**Assignment:** Backend Engineering - Google Sheets to PostgreSQL/NeonDB Migration
**Timeline:** December 14-16, 2025
**Candidate:** Yash

---

## Table of Contents
1. [Project Setup](#project-setup)
2. [Task 1: Environment Setup](#task-1-environment-setup)
3. [Task 2: Data Audit](#task-2-data-audit)
4. [Task 3: Database Design](#task-3-database-design)
5. [Task 4: ETL Pipeline](#task-4-etl-pipeline)
6. [Task 5: SQL Development](#task-5-sql-development)
7. [Task 6: App Script Automation](#task-6-app-script-automation)
8. [Task 7: Public Dataset Practice](#task-7-public-dataset-practice)
9. [Errors & Solutions](#errors--solutions)
10. [Final Deliverables](#final-deliverables)

---

## Project Setup

### Date: December 14, 2025

**Actions Taken:**
- Initialized Git repository
- Created GitHub remote: `https://github.com/YashSensei/SDE_intern_assingment.git`
- Created project folder structure

**Tech Stack:**
- **Database:** NeonDB (serverless PostgreSQL 17.7)
- **ETL Language:** Python 3.x
- **Key Libraries:** pandas, psycopg2-binary, google-api-python-client, Flask
- **ER Diagram Tool:** dbdiagram.io
- **Documentation:** Notion + Markdown

---

## Task 1: Environment Setup

**Status:** COMPLETE

### Phase 1A: NeonDB Setup
1. Created NeonDB account and project
2. Obtained connection credentials
3. Created `.env` file with credentials
4. Created Python virtual environment
5. Installed all required packages
6. Successfully tested database connection

**Connection Details:**
- Database: NeonDB (PostgreSQL 17.7)
- Connection Status: PASSED

**Files Created:**
- `.env` (credentials, gitignored)
- `etl/test_connection.py`
- `etl/requirements.txt`

### Phase 1B: Google Cloud Setup
**Status:** COMPLETE
- Google Cloud Project created
- Google Sheets API enabled
- Service account credentials configured
- `credentials.json` in place

---

## Task 2: Data Audit

**Status:** COMPLETE

**Files Created:**
- `etl/data_audit.py` - Data quality analysis script
- `datasets/messy_students_raw.csv` - Sample messy data (16 records)

**Data Issues Identified:**
1. **Duplicates:** Student ID 5 appears twice (Charlie Brown)
2. **Missing Values:**
   - Row 4: Missing email
   - Row 9: Missing last name
   - Row 8: Missing phone
3. **Inconsistent Formatting:**
   - Department: "CS", "CompSci", "Computer Science" (same dept, different names)
   - Status: "active", "Active", "ACTIVE" (case variations)
   - Phone: "555-0101", "5550102", "(555) 011-0103" (format variations)
   - DOB: "2003-05-15", "08/22/2004", "11-30-2002" (date format variations)
4. **Invalid Data:**
   - Row 12: Year level 5 (should be 1-4)
   - Row 15: Invalid email format "INVALID.EMAIL"

**Column Mapping Document:**
| Source Column | Target Column | Transformation |
|--------------|---------------|----------------|
| Student ID | student_id | Direct mapping |
| Email | student_email | Lowercase, validate format |
| First Name | first_name | Trim whitespace |
| Last Name | last_name | Trim whitespace |
| Year | year_level | Convert to int, clamp 1-4 |
| Department | department_id | Map to department lookup |
| Status | enrollment_status | Normalize case |
| Phone | phone_number | Standardize format |
| DOB | date_of_birth | Parse multiple formats |

---

## Task 3: Database Design

**Status:** COMPLETE

### Schema (3NF Normalized)

**Entities:**
- **departments** (5 records)
  - Primary Key: department_id
  - Fields: department_name, department_head, building

- **students** (15 records)
  - Primary Key: student_id
  - Foreign Key: department_id
  - Unique: student_email
  - Fields: first_name, last_name, year_level, enrollment_status, phone_number, date_of_birth

- **courses** (16 records)
  - Primary Key: course_id
  - Foreign Key: department_id
  - Unique: course_code
  - Fields: course_name, credits, max_capacity, semester

- **enrollments** (32 records)
  - Primary Key: enrollment_id
  - Foreign Keys: student_id, course_id
  - Unique: (student_id, course_id)
  - Fields: enrollment_date, grade, grade_points, attendance_percentage, status

### Indexes Created
- `idx_students_department` - FK index
- `idx_courses_department` - FK index
- `idx_enrollments_student` - FK index
- `idx_enrollments_course` - FK index
- `idx_students_email` - Email lookup
- `idx_students_status` - Status filtering
- `idx_courses_code` - Course code lookup
- `idx_enrollments_status` - Status filtering
- `idx_students_dept_year` - Composite for reports
- `idx_enrollments_student_status` - Composite for queries

### Triggers
- Auto-update `updated_at` timestamp on all tables

**Files Created:**
- `sql/schema.sql` - Table definitions with indexes
- `sql/seed.sql` - Sample data (68 records)
- `sql/reset_db.sql` - Database reset utility
- `sql/deploy.py` - Automated deployment

---

## Task 4: ETL Pipeline

**Status:** COMPLETE

### ETL Architecture

```
[Google Sheets / CSV]
        |
        v
    EXTRACT
    - Google Sheets API
    - CSV file fallback
        |
        v
    TRANSFORM
    - Remove duplicates
    - Normalize columns
    - Validate emails
    - Map departments
    - Clean phone numbers
    - Parse dates
    - Validate year levels
        |
        v
    LOAD
    - Upsert departments
    - Insert/Update students
    - Transaction handling
        |
        v
    [NeonDB PostgreSQL]
```

### Key Features
- **Deduplication:** Removes duplicate records by Student ID
- **Data Validation:** Email format, year level range, GPA range
- **Normalization:** Department name mapping, status standardization
- **Error Handling:** Comprehensive logging, validation error reporting
- **Incremental Support:** Upserts existing records

### Files Created
- `etl/etl.py` - Main ETL pipeline (500+ lines)
- `etl/config.py` - Configuration settings
- `etl/api.py` - REST API for Google App Script integration

### Usage
```bash
# Run ETL from Google Sheets
python etl/etl.py --source sheets

# Run ETL from CSV (testing)
python etl/etl.py --source csv --csv-path datasets/messy_students_raw.csv
```

### Sample Output
```
[PHASE 1/3] EXTRACT
Extracted 16 records from Google Sheets

[PHASE 2/3] TRANSFORM
Transformation complete: 16 -> 14 records
Duplicates removed: 2
Validation errors: 2

[PHASE 3/3] LOAD
Departments inserted: 0
Students inserted: 12
Students updated: 2

ETL PIPELINE COMPLETED SUCCESSFULLY
```

---

## Task 5: SQL Development

**Status:** COMPLETE

### Files Created

#### `sql/queries.sql` - 15 Complex Queries
1. Students per department (COUNT)
2. Average GPA per course (AVG, GROUP BY)
3. Students per year level with GPA
4. Student transcript (multi-table JOIN)
5. Cross-department enrollments
6. Course enrollment summary
7. Duplicate email detection
8. Data validation query
9. Invalid enrollment detection
10. Department performance report
11. Top performing students
12. Course pass rates
13. Student enrollment summary
14. Semester-wise trends
15. Student workload analysis

#### `sql/views.sql` - 8 Views
**Regular Views:**
- `vw_student_overview` - Student info with enrollment stats
- `vw_course_enrollment_summary` - Course statistics
- `vw_department_stats` - Department-level metrics
- `vw_student_transcript` - Detailed transcript
- `vw_active_enrollments` - Current enrollments
- `vw_at_risk_students` - Academic intervention list

**Materialized Views:**
- `mv_department_dashboard` - Pre-computed department stats
- `mv_course_performance` - Pre-computed course metrics

#### `sql/procedures.sql` - 10 Stored Procedures
1. `sp_register_student()` - Register new student with validation
2. `sp_update_student_status()` - Update student status
3. `sp_enroll_student()` - Enroll in course with capacity check
4. `sp_drop_course()` - Drop/withdraw from course
5. `sp_record_grade()` - Record final grade
6. `sp_get_student_gpa()` - Calculate cumulative GPA
7. `sp_department_report()` - Department statistics
8. `sp_batch_complete_semester()` - Batch operations
9. `sp_auto_assign_courses()` - Auto-enroll in default courses
10. `sp_validate_data_integrity()` - Data quality checks

---

## Task 6: App Script Automation

**Status:** COMPLETE

### Files Created
- `google-app-script/auto_register.gs` - Complete automation script

### Features
1. **Trigger on Edit:** Automatically processes new rows
2. **Data Validation:**
   - Email format validation
   - Required field checks
   - Year level validation (1-4)
   - Department validation
3. **Auto-Registration:** Inserts valid students into NeonDB
4. **Error Handling:**
   - Row highlighting for errors
   - Email notifications for failures
5. **Visual Feedback:**
   - Green highlight for processed rows
   - Red highlight for errors
   - Status column tracking

### REST API Endpoint
- `etl/api.py` provides `/register` endpoint for App Script
- Supports student creation and update
- Returns JSON responses

### Setup Instructions
1. Open Google Sheet
2. Extensions > Apps Script
3. Paste code from `auto_register.gs`
4. Update CONFIG with NeonDB credentials
5. Run `setupTrigger()` once

---

## Task 7: Public Dataset Practice

**Status:** COMPLETE

### Files Created
- `etl/public_datasets_etl.py` - ETL for 2 public datasets

### Dataset 1: Iris Dataset (Clean/Normalized)
- **Source:** UCI Machine Learning Repository
- **Records:** 150
- **Schema:** `iris_data` table with species classification data
- **Demonstrates:** Clean data ETL with minimal transformation

### Dataset 2: Movies Dataset (Messy JSON)
- **Source:** Sample movie data (simulating real-world messy data)
- **Records:** 10 (with duplicates, missing values)
- **Schema:**
  - `movies` table (normalized)
  - `movie_genres` table (many-to-many)
- **Demonstrates:**
  - Nested JSON handling
  - Data type conversions ("142 min" -> 142)
  - Money format cleaning ("$185,000,000" -> 185000000)
  - Duplicate removal
  - Genre normalization

### Optimization Demonstrations
- Index usage verification with EXPLAIN ANALYZE
- Query performance benchmarks
- Materialized view refresh

### Usage
```bash
python etl/public_datasets_etl.py
```

---

## Errors & Solutions

### Error #1: Duplicate Key Violation
**Context:** seed.sql deployment
**Error:** `duplicate key value violates unique constraint`
**Solution:** Removed duplicate enrollment, added reset_db.sql

### Error #2: Git Tracking .venv
**Context:** `git status` showed thousands of files
**Solution:** Added `.venv/` to `.gitignore`

### Error #3: Date Parsing Failures
**Context:** Multiple date formats in source data
**Solution:** Implemented multi-format date parser with fallback

---

## Final Deliverables

- [x] Working NeonDB schema with 4 tables
- [x] Functional ETL pipeline (etl.py)
- [x] Auto-registration App Script (auto_register.gs)
- [x] SQL queries, views, and procedures
- [x] Public dataset ETL examples
- [x] Test suite (tests/test_etl.py)
- [x] REST API for App Script integration
- [x] Comprehensive documentation
- [ ] Notion documentation (user to create)
- [ ] Presentation slides (user to create)
- [ ] ER Diagram image (user to create in dbdiagram.io)

---

## File Structure (Final)

```
sde_intern_assignment/
├── README.md
├── BUILD_LOG.md
├── CLAUDE.md
├── .env.example
├── .gitignore
│
├── sql/
│   ├── schema.sql          # Table definitions
│   ├── seed.sql            # Sample data
│   ├── reset_db.sql        # Database reset
│   ├── deploy.py           # Deployment script
│   ├── queries.sql         # Complex queries
│   ├── views.sql           # Views & materialized views
│   └── procedures.sql      # Stored procedures
│
├── etl/
│   ├── etl.py              # Main ETL pipeline
│   ├── config.py           # Configuration
│   ├── api.py              # REST API server
│   ├── test_connection.py  # DB connection test
│   ├── test_sheets_connection.py
│   ├── data_audit.py       # Data quality analysis
│   ├── public_datasets_etl.py  # Public dataset ETL
│   ├── requirements.txt    # Python dependencies
│   └── logs/               # ETL execution logs
│
├── google-app-script/
│   └── auto_register.gs    # App Script automation
│
├── datasets/
│   └── messy_students_raw.csv
│
├── tests/
│   └── test_etl.py         # Unit tests
│
└── docs/
    └── VERIFICATION_CHECKLIST.md
```

---

**Last Updated:** December 15, 2025
**Status:** Implementation Complete - Ready for Testing & Presentation
