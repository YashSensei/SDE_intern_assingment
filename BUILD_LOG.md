# 🚀 SDE Intern Assignment - Build Log

**Assignment:** Backend Engineering - Google Sheets to PostgreSQL/NeonDB Migration  
**Timeline:** December 14-16, 2025  
**Candidate:** Yash

---

## 📋 Table of Contents
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

## 🎯 Project Setup

### Date: December 14, 2025 - 00:00

**Actions Taken:**
- ✅ Initialized Git repository
- ✅ Created GitHub remote: `https://github.com/YashSensei/SDE_intern_assingment.git`
- ✅ Created project folder structure:
  ```
  sde_intern_assignment/
  ├── README.md
  ├── BUILD_LOG.md (this file)
  ├── sql/
  ├── etl/
  │   └── logs/
  ├── docs/
  ├── google-app-script/
  ├── datasets/
  └── tests/
  ```

**Tech Stack Decisions:**
- **Database:** NeonDB (serverless PostgreSQL)
- **ETL Language:** Python 3.x
- **Key Libraries:** pandas, psycopg2-binary, google-api-python-client
- **ER Diagram Tool:** dbdiagram.io
- **Documentation:** Notion + Markdown

**Next Steps:**
- Set up NeonDB account
- Configure Google Cloud Project
- Create test connection scripts

---

## 📝 Task 1: Environment Setup

### Phase 1A: NeonDB Setup
**Status:** ✅ Complete

**Actions Completed:**
1. ✅ Created NeonDB account and project
2. ✅ Obtained connection credentials
3. ✅ Created `.env` file with credentials
4. ✅ Created Python virtual environment
5. ✅ Installed all required packages:
   - psycopg2-binary (PostgreSQL adapter)
   - pandas & numpy (data manipulation)
   - google-api-python-client (Sheets API)
   - python-dotenv (environment variables)
   - pytest (testing framework)
6. ✅ Successfully tested database connection

**Connection Details:**
- Database: NeonDB (PostgreSQL 17.7)
- Host: ep-delicate-hall-ad0dwnzr-pooler.c-2.us-east-1.aws.neon.tech
- Database Name: neondb
- User: neondb_owner
- Connection Status: ✅ PASSED

**Files Created:**
- `.env` (credentials, gitignored)
- `etl/test_connection.py` (connection test script)
- `etl/requirements.txt` (Python dependencies)

---

### Phase 1B: Google Cloud Setup
**Status:** 🟡 In Progress

**Required Actions (User):**

**Step 1: Create Google Cloud Project**
1. Go to https://console.cloud.google.com/
2. Click "New Project" in the top navigation
3. Project Name: "SDE-Intern-Assignment"
4. Click "Create"

**Step 2: Enable Google Sheets API**
1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"

**Step 3: Create Service Account**
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Service Account Name: "sheets-etl-service"
4. Click "Create and Continue"
5. Grant role: "Editor" (for now)
6. Click "Done"

**Step 4: Create & Download JSON Key**
1. Click on the newly created service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Choose "JSON" format
5. Click "Create" → File will download automatically
6. **IMPORTANT:** Save this file as `credentials.json` in your project root

**Step 5: Share Google Sheet**
1. Open the JSON file and find the "client_email" field (looks like: xxx@xxx.iam.gserviceaccount.com)
2. Copy this email address
3. You'll use this to share your Google Sheets later

**What I'll Do Next:**
- Create test Google Sheets script
- Verify API access
- Create sample "messy" student data sheet

---

## 🔍 Task 2: Data Audit

**Status:** 🔜 Pending (Requires Google Sheets setup)

(Will be updated after Google Cloud credentials are configured...)

---

## 🗂️ Task 3: Database Design

**Status:** ✅ Complete

**Actions Completed:**
1. ✅ Designed normalized database schema (3NF)
2. ✅ Created entity-relationship model
3. ✅ Implemented schema with proper constraints
4. ✅ Added indexes for optimization
5. ✅ Created seed data with realistic records
6. ✅ Successfully deployed to NeonDB

**Schema Details:**

**Entities:**
- **departments** (5 records)
  - Primary Key: department_id
  - Contains: CS, Math, Physics, Business, Engineering
  
- **students** (15 records)
  - Primary Key: student_id
  - Foreign Key: department_id → departments
  - Unique constraint on email
  - Includes: active, graduated, inactive statuses
  
- **courses** (16 records)
  - Primary Key: course_id
  - Foreign Key: department_id → departments
  - Course codes follow pattern: DEPT###
  
- **enrollments** (32 records)
  - Primary Key: enrollment_id
  - Foreign Keys: student_id → students, course_id → courses
  - Unique constraint: (student_id, course_id)
  - Supports: enrolled, completed, withdrawn, dropped statuses

**Relationships:**
- Department → Students (One-to-Many)
- Department → Courses (One-to-Many)
- Student ↔ Course through Enrollments (Many-to-Many)

**Optimizations Applied:**
- Indexes on all foreign keys
- Composite unique index on (student_id, course_id)
- CHECK constraints for grade validation
- Timestamp tracking with automatic updates

**Files Created:**
- `sql/schema.sql` - Complete table definitions
- `sql/seed.sql` - Sample data with 68 total records
- `sql/reset_db.sql` - Database reset utility
- `sql/deploy.py` - Automated deployment script

**Deployment Status:**
```
✅ Departments:  5 records
✅ Students:    15 records
✅ Courses:     16 records
✅ Enrollments: 32 records
```

**ER Diagram:** (To be created in dbdiagram.io)

---

## 🔄 Task 4: ETL Pipeline

**Status:** 🔜 Not Started

(Will be updated as we progress...)

---

## 💾 Task 5: SQL Development

**Status:** 🔜 Not Started

(Will be updated as we progress...)

---

## ⚡ Task 6: App Script Automation

**Status:** 🔜 Not Started

(Will be updated as we progress...)

---

## 📊 Task 7: Public Dataset Practice

**Status:** 🔜 Not Started

(Will be updated as we progress...)

---

## ❌ Errors & Solutions

### Error Log

**Error #1: Duplicate Key Violation During Seed Deployment**
**Date:** December 14, 2025  
**Context:** Running `python sql/deploy.py` - seed.sql insert failed  
**Error Message:**
```
duplicate key value violates unique constraint "enrollments_student_id_course_id_key"
DETAIL: Key (student_id, course_id)=(4, 6) already exists.
```
**Root Cause:** seed.sql contained duplicate enrollment records for student_id=4, course_id=6:
- Line 105: `(4, 6, '2023-08-20', 'B', 3.00, 80.00, 'completed')`
- Line 151: `(4, 6, '2024-01-15', NULL, NULL, 30.00, 'dropped')`

**Solution:** 
1. Removed the duplicate entry on line 105
2. Kept only the dropped enrollment record to show realistic scenario
3. Added `reset_db.sql` to ensure clean deployments
4. Updated `deploy.py` to call reset before schema deployment

**Prevention:** 
- Review seed data for duplicates before deployment
- Use composite unique constraints to catch duplicates
- Implement automated tests for seed data validation

---

**Error #2: Git Tracking 5000+ Files from .venv/**
**Date:** December 14, 2025  
**Context:** `git status` showed thousands of changes  
**Root Cause:** `.venv/` directory not in `.gitignore`  
**Solution:** Added `.venv/` to `.gitignore`  
**Prevention:** Always add virtual environment folders to `.gitignore` immediately after creation

---

## ✅ Final Deliverables

- [ ] Working NeonDB schema
- [ ] Functional ETL pipeline
- [ ] Auto-registration App Script
- [ ] Notion documentation
- [ ] Presentation slides
- [ ] GitHub repository with all code
- [ ] Demo video/screenshots

---

**Last Updated:** December 14, 2025
