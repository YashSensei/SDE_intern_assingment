-- ============================================
-- SDE Intern Assignment - Database Schema
-- Database: NeonDB (PostgreSQL 17.7)
-- Purpose: Student Management System
-- Normalization: 3NF
-- ============================================

-- Drop tables if they exist (for clean rebuild)
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- ============================================
-- Table: departments
-- Description: Academic departments
-- ============================================
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_head VARCHAR(100),
    building VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Table: students
-- Description: Student information
-- ============================================
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    student_email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    year_level INTEGER CHECK (year_level BETWEEN 1 AND 4),
    department_id INTEGER REFERENCES departments(department_id) ON DELETE SET NULL,
    enrollment_status VARCHAR(20) DEFAULT 'active' CHECK (enrollment_status IN ('active', 'inactive', 'graduated', 'suspended')),
    phone_number VARCHAR(20),
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Table: courses
-- Description: Course catalog
-- ============================================
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(200) NOT NULL,
    department_id INTEGER REFERENCES departments(department_id) ON DELETE SET NULL,
    credits INTEGER NOT NULL CHECK (credits > 0),
    max_capacity INTEGER DEFAULT 50 CHECK (max_capacity > 0),
    semester VARCHAR(20) CHECK (semester IN ('Fall', 'Spring', 'Summer')),
    course_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Table: enrollments
-- Description: Student course enrollments (many-to-many relationship)
-- ============================================
CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    grade VARCHAR(2) CHECK (grade IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F', 'W', 'I', NULL)),
    grade_points DECIMAL(3,2) CHECK (grade_points BETWEEN 0.00 AND 4.00),
    attendance_percentage DECIMAL(5,2) CHECK (attendance_percentage BETWEEN 0.00 AND 100.00),
    status VARCHAR(20) DEFAULT 'enrolled' CHECK (status IN ('enrolled', 'completed', 'dropped', 'withdrawn')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate enrollments
    UNIQUE (student_id, course_id)
);

-- ============================================
-- INDEXES for Performance Optimization
-- ============================================

-- Foreign key indexes
CREATE INDEX idx_students_department ON students(department_id);
CREATE INDEX idx_courses_department ON courses(department_id);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);

-- Commonly queried fields
CREATE INDEX idx_students_email ON students(student_email);
CREATE INDEX idx_students_status ON students(enrollment_status);
CREATE INDEX idx_courses_code ON courses(course_code);
CREATE INDEX idx_courses_semester ON courses(semester);
CREATE INDEX idx_enrollments_status ON enrollments(status);
CREATE INDEX idx_enrollments_grade ON enrollments(grade);

-- Composite indexes for common queries
CREATE INDEX idx_students_dept_year ON students(department_id, year_level);
CREATE INDEX idx_enrollments_student_status ON enrollments(student_id, status);

-- ============================================
-- TRIGGERS for Automatic Timestamp Updates
-- ============================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_departments_updated_at
    BEFORE UPDATE ON departments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courses_updated_at
    BEFORE UPDATE ON courses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enrollments_updated_at
    BEFORE UPDATE ON enrollments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- COMMENTS for Documentation
-- ============================================

COMMENT ON TABLE departments IS 'Academic departments within the university';
COMMENT ON TABLE students IS 'Student registration and personal information';
COMMENT ON TABLE courses IS 'Course catalog with department associations';
COMMENT ON TABLE enrollments IS 'Student-course enrollments with grades and status';

COMMENT ON COLUMN students.enrollment_status IS 'Current enrollment status: active, inactive, graduated, suspended';
COMMENT ON COLUMN enrollments.grade_points IS 'GPA points: A+=4.0, A=4.0, A-=3.7, B+=3.3, etc.';
COMMENT ON COLUMN enrollments.status IS 'Enrollment status: enrolled, completed, dropped, withdrawn';

-- ============================================
-- Schema Creation Complete
-- ============================================
