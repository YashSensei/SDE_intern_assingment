# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a backend engineering assignment demonstrating migration from Google Sheets-based workflows to a production-grade PostgreSQL/NeonDB infrastructure. The project includes:
- Automated ETL pipelines (Google Sheets → PostgreSQL)
- Normalized database design (3NF)
- Google App Script automation for auto-registration
- SQL optimization with views, procedures, and indexes
- REST API for external integrations

## Common Development Commands

### Database Operations
```bash
# Test database connection
python etl/test_connection.py

# Deploy schema and seed data
python sql/deploy.py

# Test Google Sheets connection
python etl/test_sheets_connection.py
```

### ETL Pipeline
```bash
# Run ETL from Google Sheets (production)
python etl/etl.py --source sheets

# Run ETL from CSV (testing)
python etl/etl.py --source csv --csv-path datasets/messy_students_raw.csv

# Run data audit on Google Sheets
python etl/data_audit.py

# Load public datasets (Iris + Movies)
python etl/public_datasets_etl.py
```

### API Server
```bash
# Start REST API server (for Google App Script integration)
python etl/api.py
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_etl.py -v
```

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r etl/requirements.txt
```

## Architecture Overview

### Database Schema (NeonDB/PostgreSQL)
Four normalized tables in 3NF:

```
departments (1) ──────< students (N)
     │                      │
     │                      │
     v                      v
courses (N) >────── enrollments ──────< students
```

- **departments**: Academic departments (CS, Math, Physics, etc.)
- **students**: Student records with department FK
- **courses**: Course catalog with department FK
- **enrollments**: Many-to-many between students and courses

### ETL Pipeline Flow
```
[Google Sheets] → EXTRACT → TRANSFORM → LOAD → [NeonDB]
                     │           │         │
                     │           │         └── Upsert logic
                     │           └── Validation, normalization, deduplication
                     └── Google Sheets API or CSV fallback
```

### Key Files

| File | Purpose |
|------|---------|
| `etl/etl.py` | Main ETL pipeline with Extract/Transform/Load phases |
| `etl/api.py` | Flask REST API for Google App Script integration |
| `etl/config.py` | Centralized configuration |
| `sql/schema.sql` | Table definitions with indexes and triggers |
| `sql/queries.sql` | 15 complex SQL queries |
| `sql/views.sql` | 6 regular views + 2 materialized views |
| `sql/procedures.sql` | 10 stored procedures |
| `google-app-script/auto_register.gs` | Auto-registration workflow |

## Configuration

### Required Environment Variables (.env)
```
DB_HOST=your-project.neon.tech
DB_NAME=neondb
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432

GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SHEET_NAME=Sheet1
```

### Department Mapping
The ETL normalizes department name variations:
- "CS", "CompSci" → "Computer Science"
- "Math" → "Mathematics"
- "EE" → "Electrical Engineering"
- "Business" → "Business Administration"

## API Endpoints

### POST /register
Register or update a student:
```json
{
  "email": "student@university.edu",
  "first_name": "John",
  "last_name": "Doe",
  "year_level": 1,
  "department": "Computer Science",
  "status": "active",
  "phone": "555-1234",
  "dob": "2005-01-15"
}
```

### GET /students
List all students

### GET /students/{id}
Get specific student

## Testing

The test suite covers:
- Email validation
- Department name mapping
- Status normalization
- Year level validation
- Phone number formatting
- Date parsing
- GPA validation
- Duplicate removal

## Stored Procedures

Key procedures for common operations:
- `sp_register_student()` - Register with validation
- `sp_enroll_student()` - Enroll with capacity check
- `sp_record_grade()` - Record final grade
- `sp_get_student_gpa()` - Calculate cumulative GPA
- `sp_validate_data_integrity()` - Data quality checks

## Google App Script Integration

The `auto_register.gs` script:
1. Triggers on new row in Google Sheet
2. Validates data (email, year level, department)
3. Calls REST API to register student
4. Highlights row green (success) or red (error)
5. Sends email notification on failure
