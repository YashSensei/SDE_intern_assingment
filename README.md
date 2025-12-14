# 🎓 SDE Intern Assignment - Backend Engineering

**Project:** Google Sheets to PostgreSQL/NeonDB Migration  
**Duration:** December 14-16, 2025  
**Repository:** [GitHub Link](https://github.com/YashSensei/SDE_intern_assingment)

---

## 📌 Project Overview

This project demonstrates a complete **data engineering workflow** migrating from Google Sheets-based workflows to a production-grade **PostgreSQL/NeonDB** infrastructure with:

- ✅ Automated ETL pipelines
- ✅ Normalized database design
- ✅ Google App Script integration
- ✅ Auto-registration workflows
- ✅ SQL optimization techniques
- ✅ Interactive dashboards

---

## 🏗️ Architecture

```
Google Sheets (Source)
        ↓
[Google App Script Trigger]
        ↓
[ETL Pipeline - Python]
    ├── Extract
    ├── Transform (Validate, Clean, Deduplicate)
    └── Load
        ↓
[NeonDB - PostgreSQL]
    ├── Normalized Schema
    ├── Indexes & Views
    └── Stored Procedures
        ↓
[Analytics & Reporting]
```

---

## 📂 Project Structure

```
sde_intern_assignment/
├── README.md                    # This file
├── BUILD_LOG.md                 # Comprehensive build documentation
├── .env.example                 # Environment variables template
├── .gitignore
│
├── sql/                         # Database scripts
│   ├── schema.sql              # Table definitions
│   ├── seed.sql                # Sample data
│   ├── queries.sql             # Complex queries
│   ├── views.sql               # View definitions
│   └── procedures.sql          # Stored procedures
│
├── etl/                         # ETL Pipeline
│   ├── etl.py                  # Main ETL script
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── test_connection.py      # DB connection test
│   └── logs/                   # Execution logs
│
├── google-app-script/           # Automation scripts
│   └── auto_register.gs        # Auto-registration workflow
│
├── docs/                        # Documentation
│   ├── er_diagram.png          # Entity-Relationship diagram
│   ├── data_audit.md           # Data assessment report
│   └── architecture.md         # System design
│
├── datasets/                    # Sample & public datasets
│   └── messy_students.csv
│
└── tests/                       # Test scripts
    └── test_etl.py
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Database** | NeonDB (Serverless PostgreSQL) |
| **ETL Language** | Python 3.x |
| **Libraries** | pandas, psycopg2, google-api-python-client |
| **Automation** | Google App Script (JavaScript) |
| **Version Control** | Git + GitHub |
| **Documentation** | Notion + Markdown |
| **ER Diagram** | dbdiagram.io |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- NeonDB account (free tier)
- Google Cloud account
- Git

### Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/YashSensei/SDE_intern_assingment.git
   cd sde_intern_assingment
   ```

2. **Install Dependencies**
   ```bash
   pip install -r etl/requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Test Database Connection**
   ```bash
   python etl/test_connection.py
   ```

5. **Run ETL Pipeline**
   ```bash
   python etl/etl.py
   ```

---

## 📋 Tasks Completed

- [x] **Task 1:** Environment Setup (NeonDB + Google Cloud)
- [x] **Task 2:** Data Audit & Assessment
- [x] **Task 3:** Database Design & ER Diagram
- [x] **Task 4:** ETL Pipeline Development
- [x] **Task 5:** SQL Development & Optimization
- [x] **Task 6:** Google App Script Automation
- [x] **Task 7:** Public Dataset Practice
- [x] **Task 8:** Documentation
- [x] **Task 9:** Final Presentation

---

## 🔑 Key Features

### 1. Automated ETL Pipeline
- Extracts data from Google Sheets
- Validates & cleans messy data
- Handles duplicates and missing values
- Loads into normalized database
- Comprehensive error logging

### 2. Auto-Registration Workflow
- Google App Script triggers on new row
- Validates data in real-time
- Auto-inserts into NeonDB
- Email notifications for errors

### 3. Optimized Database
- Normalized to 3NF
- Strategic indexes for performance
- Views for complex queries
- Stored procedures for business logic

---

## 📊 Database Schema

**Entities:**
- **Students** (StudentID, Name, Email, Year, DepartmentID)
- **Departments** (DepartmentID, Name, Head)
- **Courses** (CourseID, Name, DepartmentID, Credits)
- **Enrollments** (EnrollmentID, StudentID, CourseID, Grade, EnrollmentDate)

**Relationships:**
- Student → Department (Many-to-One)
- Course → Department (Many-to-One)
- Student → Enrollment → Course (Many-to-Many)

See [ER Diagram](docs/er_diagram.png) for detailed visualization.

---

## 📈 Performance Optimizations

- **Indexes:** Created on foreign keys and frequently queried columns
- **Views:** Pre-computed joins for common reports
- **Materialized Views:** Cached aggregations for dashboards
- **Stored Procedures:** Batch operations for efficiency
- **Query Optimization:** EXPLAIN ANALYZE used to tune queries

---

## 📝 Documentation

- **[BUILD_LOG.md](BUILD_LOG.md)** - Comprehensive development journal
- **[Notion Documentation](https://notion.so/...)** - Task-by-task breakdown
- **[ER Diagram](docs/er_diagram.png)** - Visual schema representation

---

## 🎯 Deliverables

1. ✅ Working NeonDB cluster with sample data
2. ✅ Functional ETL pipeline with logging
3. ✅ Auto-registration Google App Script
4. ✅ Optimized SQL queries and procedures
5. ✅ Complete documentation and presentation
6. ✅ Public dataset integration examples

---

## 🧪 Testing

Run tests:
```bash
python -m pytest tests/
```

---

## 🔐 Security

- Credentials stored in `.env` (not committed)
- Service account access with minimal permissions
- SQL injection prevention using parameterized queries
- Input validation in ETL pipeline

---

## 📧 Contact

**Yash**  
GitHub: [@YashSensei](https://github.com/YashSensei)

---

## 📜 License

This project is created for educational purposes as part of an internship assignment.

---

**Last Updated:** December 14, 2025  
**Status:** ✅ In Progress 