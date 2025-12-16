-- ============================================
-- SDE Intern Assignment - Stored Procedures
-- Task 5: SQL Development & Optimization
-- ============================================

-- ============================================
-- STUDENT MANAGEMENT PROCEDURES
-- ============================================

-- 1. Register New Student
CREATE OR REPLACE FUNCTION sp_register_student(
    p_email VARCHAR(255),
    p_first_name VARCHAR(50),
    p_last_name VARCHAR(50),
    p_year_level INTEGER,
    p_department_name VARCHAR(100),
    p_phone VARCHAR(20) DEFAULT NULL,
    p_dob DATE DEFAULT NULL
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    student_id INTEGER
) AS $$
DECLARE
    v_dept_id INTEGER;
    v_student_id INTEGER;
BEGIN
    -- Validate email format
    IF p_email !~ '^[\w\.-]+@[\w\.-]+\.\w+$' THEN
        RETURN QUERY SELECT FALSE, 'Invalid email format', NULL::INTEGER;
        RETURN;
    END IF;

    -- Check if email already exists
    IF EXISTS (SELECT 1 FROM students WHERE student_email = p_email) THEN
        RETURN QUERY SELECT FALSE, 'Email already registered', NULL::INTEGER;
        RETURN;
    END IF;

    -- Validate year level
    IF p_year_level NOT BETWEEN 1 AND 4 THEN
        RETURN QUERY SELECT FALSE, 'Year level must be between 1 and 4', NULL::INTEGER;
        RETURN;
    END IF;

    -- Get department ID
    SELECT department_id INTO v_dept_id
    FROM departments
    WHERE LOWER(department_name) = LOWER(p_department_name);

    IF v_dept_id IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Department not found: ' || p_department_name, NULL::INTEGER;
        RETURN;
    END IF;

    -- Insert student
    INSERT INTO students (
        student_email, first_name, last_name, year_level,
        department_id, enrollment_status, phone_number, date_of_birth
    ) VALUES (
        LOWER(p_email), p_first_name, p_last_name, p_year_level,
        v_dept_id, 'active', p_phone, p_dob
    )
    RETURNING students.student_id INTO v_student_id;

    RETURN QUERY SELECT TRUE, 'Student registered successfully', v_student_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_register_student IS 'Register a new student with validation';

-- 2. Update Student Status
CREATE OR REPLACE FUNCTION sp_update_student_status(
    p_student_id INTEGER,
    p_new_status VARCHAR(20)
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT
) AS $$
BEGIN
    -- Validate status
    IF p_new_status NOT IN ('active', 'inactive', 'graduated', 'suspended') THEN
        RETURN QUERY SELECT FALSE, 'Invalid status. Must be: active, inactive, graduated, or suspended';
        RETURN;
    END IF;

    -- Check if student exists
    IF NOT EXISTS (SELECT 1 FROM students WHERE student_id = p_student_id) THEN
        RETURN QUERY SELECT FALSE, 'Student not found';
        RETURN;
    END IF;

    -- Update status
    UPDATE students
    SET enrollment_status = p_new_status,
        updated_at = CURRENT_TIMESTAMP
    WHERE student_id = p_student_id;

    RETURN QUERY SELECT TRUE, 'Status updated to: ' || p_new_status;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ENROLLMENT MANAGEMENT PROCEDURES
-- ============================================

-- 3. Enroll Student in Course
CREATE OR REPLACE FUNCTION sp_enroll_student(
    p_student_id INTEGER,
    p_course_code VARCHAR(20)
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    enrollment_id INTEGER
) AS $$
DECLARE
    v_course_id INTEGER;
    v_max_capacity INTEGER;
    v_current_enrolled INTEGER;
    v_enrollment_id INTEGER;
BEGIN
    -- Get course info
    SELECT course_id, max_capacity INTO v_course_id, v_max_capacity
    FROM courses
    WHERE course_code = p_course_code;

    IF v_course_id IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Course not found: ' || p_course_code, NULL::INTEGER;
        RETURN;
    END IF;

    -- Check if student exists and is active
    IF NOT EXISTS (
        SELECT 1 FROM students
        WHERE student_id = p_student_id AND enrollment_status = 'active'
    ) THEN
        RETURN QUERY SELECT FALSE, 'Student not found or not active', NULL::INTEGER;
        RETURN;
    END IF;

    -- Check if already enrolled
    IF EXISTS (
        SELECT 1 FROM enrollments
        WHERE student_id = p_student_id
        AND course_id = v_course_id
        AND status = 'enrolled'
    ) THEN
        RETURN QUERY SELECT FALSE, 'Student already enrolled in this course', NULL::INTEGER;
        RETURN;
    END IF;

    -- Check course capacity
    SELECT COUNT(*) INTO v_current_enrolled
    FROM enrollments
    WHERE course_id = v_course_id AND status = 'enrolled';

    IF v_current_enrolled >= v_max_capacity THEN
        RETURN QUERY SELECT FALSE, 'Course is at full capacity', NULL::INTEGER;
        RETURN;
    END IF;

    -- Create enrollment
    INSERT INTO enrollments (
        student_id, course_id, enrollment_date, status
    ) VALUES (
        p_student_id, v_course_id, CURRENT_DATE, 'enrolled'
    )
    RETURNING enrollments.enrollment_id INTO v_enrollment_id;

    RETURN QUERY SELECT TRUE, 'Successfully enrolled in ' || p_course_code, v_enrollment_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_enroll_student IS 'Enroll a student in a course with capacity checks';

-- 4. Drop Course
CREATE OR REPLACE FUNCTION sp_drop_course(
    p_student_id INTEGER,
    p_course_code VARCHAR(20),
    p_reason VARCHAR(50) DEFAULT 'dropped'
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT
) AS $$
DECLARE
    v_course_id INTEGER;
BEGIN
    -- Validate reason
    IF p_reason NOT IN ('dropped', 'withdrawn') THEN
        p_reason := 'dropped';
    END IF;

    -- Get course ID
    SELECT course_id INTO v_course_id
    FROM courses
    WHERE course_code = p_course_code;

    IF v_course_id IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Course not found';
        RETURN;
    END IF;

    -- Check if enrolled
    IF NOT EXISTS (
        SELECT 1 FROM enrollments
        WHERE student_id = p_student_id
        AND course_id = v_course_id
        AND status = 'enrolled'
    ) THEN
        RETURN QUERY SELECT FALSE, 'Student not enrolled in this course';
        RETURN;
    END IF;

    -- Update to dropped/withdrawn
    UPDATE enrollments
    SET status = p_reason,
        updated_at = CURRENT_TIMESTAMP
    WHERE student_id = p_student_id
    AND course_id = v_course_id
    AND status = 'enrolled';

    RETURN QUERY SELECT TRUE, 'Course ' || p_reason || ' successfully';
END;
$$ LANGUAGE plpgsql;

-- 5. Record Grade
CREATE OR REPLACE FUNCTION sp_record_grade(
    p_student_id INTEGER,
    p_course_code VARCHAR(20),
    p_grade VARCHAR(2),
    p_attendance DECIMAL(5,2) DEFAULT NULL
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT
) AS $$
DECLARE
    v_course_id INTEGER;
    v_grade_points DECIMAL(3,2);
BEGIN
    -- Get course ID
    SELECT course_id INTO v_course_id
    FROM courses WHERE course_code = p_course_code;

    IF v_course_id IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Course not found';
        RETURN;
    END IF;

    -- Validate grade and get grade points
    v_grade_points := CASE p_grade
        WHEN 'A+' THEN 4.00
        WHEN 'A' THEN 4.00
        WHEN 'A-' THEN 3.70
        WHEN 'B+' THEN 3.30
        WHEN 'B' THEN 3.00
        WHEN 'B-' THEN 2.70
        WHEN 'C+' THEN 2.30
        WHEN 'C' THEN 2.00
        WHEN 'C-' THEN 1.70
        WHEN 'D' THEN 1.00
        WHEN 'F' THEN 0.00
        WHEN 'W' THEN NULL  -- Withdrawn
        WHEN 'I' THEN NULL  -- Incomplete
        ELSE NULL
    END;

    IF p_grade NOT IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F', 'W', 'I') THEN
        RETURN QUERY SELECT FALSE, 'Invalid grade: ' || p_grade;
        RETURN;
    END IF;

    -- Check if enrollment exists
    IF NOT EXISTS (
        SELECT 1 FROM enrollments
        WHERE student_id = p_student_id AND course_id = v_course_id
    ) THEN
        RETURN QUERY SELECT FALSE, 'Enrollment not found';
        RETURN;
    END IF;

    -- Update enrollment with grade
    UPDATE enrollments
    SET grade = p_grade,
        grade_points = v_grade_points,
        attendance_percentage = COALESCE(p_attendance, attendance_percentage),
        status = 'completed',
        updated_at = CURRENT_TIMESTAMP
    WHERE student_id = p_student_id
    AND course_id = v_course_id;

    RETURN QUERY SELECT TRUE, 'Grade recorded: ' || p_grade || ' (' || COALESCE(v_grade_points::TEXT, 'N/A') || ' points)';
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_record_grade IS 'Record final grade for a student enrollment';

-- ============================================
-- REPORTING PROCEDURES
-- ============================================

-- 6. Get Student GPA
CREATE OR REPLACE FUNCTION sp_get_student_gpa(
    p_student_id INTEGER
)
RETURNS TABLE(
    student_name TEXT,
    completed_courses INTEGER,
    total_credits INTEGER,
    cumulative_gpa DECIMAL(3,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.first_name || ' ' || s.last_name,
        COUNT(e.enrollment_id)::INTEGER,
        COALESCE(SUM(c.credits), 0)::INTEGER,
        ROUND(AVG(e.grade_points), 2)::DECIMAL(3,2)
    FROM students s
    LEFT JOIN enrollments e ON s.student_id = e.student_id
        AND e.status = 'completed'
        AND e.grade_points IS NOT NULL
    LEFT JOIN courses c ON e.course_id = c.course_id
    WHERE s.student_id = p_student_id
    GROUP BY s.first_name, s.last_name;
END;
$$ LANGUAGE plpgsql;

-- 7. Get Department Report
CREATE OR REPLACE FUNCTION sp_department_report(
    p_department_name VARCHAR(100) DEFAULT NULL
)
RETURNS TABLE(
    department_name VARCHAR(100),
    total_students BIGINT,
    active_students BIGINT,
    total_courses BIGINT,
    avg_gpa DECIMAL(3,2),
    total_enrollments BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.department_name,
        COUNT(DISTINCT s.student_id),
        COUNT(DISTINCT s.student_id) FILTER (WHERE s.enrollment_status = 'active'),
        COUNT(DISTINCT c.course_id),
        ROUND(AVG(e.grade_points) FILTER (WHERE e.status = 'completed'), 2)::DECIMAL(3,2),
        COUNT(DISTINCT e.enrollment_id)
    FROM departments d
    LEFT JOIN students s ON d.department_id = s.department_id
    LEFT JOIN courses c ON d.department_id = c.department_id
    LEFT JOIN enrollments e ON s.student_id = e.student_id
    WHERE p_department_name IS NULL
        OR LOWER(d.department_name) = LOWER(p_department_name)
    GROUP BY d.department_id, d.department_name
    ORDER BY d.department_name;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- BATCH OPERATIONS
-- ============================================

-- 8. Batch Grade Update (for semester end)
CREATE OR REPLACE FUNCTION sp_batch_complete_semester(
    p_course_code VARCHAR(20),
    p_default_attendance DECIMAL(5,2) DEFAULT 85.0
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    students_updated INTEGER
) AS $$
DECLARE
    v_course_id INTEGER;
    v_updated INTEGER;
BEGIN
    -- Get course ID
    SELECT course_id INTO v_course_id
    FROM courses WHERE course_code = p_course_code;

    IF v_course_id IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Course not found', 0;
        RETURN;
    END IF;

    -- Update all enrolled students to have attendance if missing
    UPDATE enrollments
    SET attendance_percentage = COALESCE(attendance_percentage, p_default_attendance),
        updated_at = CURRENT_TIMESTAMP
    WHERE course_id = v_course_id
    AND status = 'enrolled'
    AND attendance_percentage IS NULL;

    GET DIAGNOSTICS v_updated = ROW_COUNT;

    RETURN QUERY SELECT TRUE,
        'Updated attendance for ' || v_updated || ' enrollments in ' || p_course_code,
        v_updated;
END;
$$ LANGUAGE plpgsql;

-- 9. Auto-Assign Default Courses for New Students
CREATE OR REPLACE FUNCTION sp_auto_assign_courses(
    p_student_id INTEGER
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT,
    courses_assigned INTEGER
) AS $$
DECLARE
    v_dept_id INTEGER;
    v_year INTEGER;
    v_courses_added INTEGER := 0;
    v_course RECORD;
BEGIN
    -- Get student info
    SELECT department_id, year_level INTO v_dept_id, v_year
    FROM students WHERE student_id = p_student_id;

    IF v_dept_id IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Student not found', 0;
        RETURN;
    END IF;

    -- Find introductory courses (101 level) from student's department
    FOR v_course IN
        SELECT course_id, course_code
        FROM courses
        WHERE department_id = v_dept_id
        AND course_code LIKE '%101'
        AND course_id NOT IN (
            SELECT course_id FROM enrollments WHERE student_id = p_student_id
        )
    LOOP
        -- Enroll in course
        INSERT INTO enrollments (student_id, course_id, status)
        VALUES (p_student_id, v_course.course_id, 'enrolled');
        v_courses_added := v_courses_added + 1;
    END LOOP;

    RETURN QUERY SELECT TRUE,
        'Auto-assigned ' || v_courses_added || ' courses',
        v_courses_added;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_auto_assign_courses IS 'Auto-enroll new students in introductory courses';

-- ============================================
-- DATA VALIDATION PROCEDURES
-- ============================================

-- 10. Validate Data Integrity
CREATE OR REPLACE FUNCTION sp_validate_data_integrity()
RETURNS TABLE(
    check_name TEXT,
    issue_count BIGINT,
    details TEXT
) AS $$
BEGIN
    -- Check for orphan enrollments
    RETURN QUERY
    SELECT
        'Orphan Enrollments'::TEXT,
        COUNT(*)::BIGINT,
        'Enrollments without valid student'::TEXT
    FROM enrollments e
    WHERE NOT EXISTS (SELECT 1 FROM students s WHERE s.student_id = e.student_id);

    -- Check for students without department
    RETURN QUERY
    SELECT
        'Students without Department'::TEXT,
        COUNT(*)::BIGINT,
        'Active students with NULL department_id'::TEXT
    FROM students
    WHERE department_id IS NULL AND enrollment_status = 'active';

    -- Check for completed courses without grades
    RETURN QUERY
    SELECT
        'Completed without Grades'::TEXT,
        COUNT(*)::BIGINT,
        'Completed enrollments missing grade'::TEXT
    FROM enrollments
    WHERE status = 'completed' AND grade IS NULL;

    -- Check for invalid GPA values
    RETURN QUERY
    SELECT
        'Invalid GPA Values'::TEXT,
        COUNT(*)::BIGINT,
        'Grade points outside 0-4 range'::TEXT
    FROM enrollments
    WHERE grade_points IS NOT NULL
    AND (grade_points < 0 OR grade_points > 4);

    -- Check for duplicate emails
    RETURN QUERY
    SELECT
        'Duplicate Emails'::TEXT,
        COUNT(*)::BIGINT,
        'Students with duplicate email addresses'::TEXT
    FROM (
        SELECT student_email FROM students
        GROUP BY student_email HAVING COUNT(*) > 1
    ) dups;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sp_validate_data_integrity IS 'Run data integrity checks on the database';

-- ============================================
-- USAGE EXAMPLES
-- ============================================

/*
-- Register a new student:
SELECT * FROM sp_register_student(
    'new.student@university.edu',
    'New',
    'Student',
    1,
    'Computer Science',
    '555-1234',
    '2005-01-15'::DATE
);

-- Enroll student in course:
SELECT * FROM sp_enroll_student(1, 'CS101');

-- Record grade:
SELECT * FROM sp_record_grade(1, 'CS101', 'A', 95.0);

-- Get student GPA:
SELECT * FROM sp_get_student_gpa(1);

-- Department report:
SELECT * FROM sp_department_report('Computer Science');

-- Validate data integrity:
SELECT * FROM sp_validate_data_integrity();
*/
