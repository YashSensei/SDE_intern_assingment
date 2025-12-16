-- ============================================
-- SDE Intern Assignment - SQL Queries
-- Task 5: SQL Development & Optimization
-- ============================================

-- ============================================
-- BASIC AGGREGATION QUERIES
-- ============================================

-- 1. Count students per department
SELECT
    d.department_name,
    COUNT(s.student_id) AS student_count
FROM departments d
LEFT JOIN students s ON d.department_id = s.department_id
GROUP BY d.department_id, d.department_name
ORDER BY student_count DESC;

-- 2. Average GPA per course (completed enrollments only)
SELECT
    c.course_code,
    c.course_name,
    COUNT(e.enrollment_id) AS total_completed,
    ROUND(AVG(e.grade_points), 2) AS average_gpa,
    MIN(e.grade_points) AS min_gpa,
    MAX(e.grade_points) AS max_gpa
FROM courses c
JOIN enrollments e ON c.course_id = e.course_id
WHERE e.status = 'completed' AND e.grade_points IS NOT NULL
GROUP BY c.course_id, c.course_code, c.course_name
ORDER BY average_gpa DESC;

-- 3. Students per year level with average GPA
SELECT
    s.year_level,
    COUNT(DISTINCT s.student_id) AS student_count,
    ROUND(AVG(e.grade_points), 2) AS avg_gpa
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id
    AND e.status = 'completed'
    AND e.grade_points IS NOT NULL
WHERE s.enrollment_status = 'active'
GROUP BY s.year_level
ORDER BY s.year_level;

-- ============================================
-- JOIN-HEAVY QUERIES (Student <-> Enrollment <-> Course)
-- ============================================

-- 4. Student transcript: All courses with grades
SELECT
    s.first_name || ' ' || s.last_name AS student_name,
    s.student_email,
    d.department_name AS student_department,
    c.course_code,
    c.course_name,
    e.grade,
    e.grade_points,
    e.attendance_percentage,
    e.status AS enrollment_status,
    e.enrollment_date
FROM students s
JOIN departments d ON s.department_id = d.department_id
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
ORDER BY s.student_id, e.enrollment_date;

-- 5. Students enrolled in courses outside their department (cross-department enrollment)
SELECT
    s.first_name || ' ' || s.last_name AS student_name,
    sd.department_name AS student_department,
    c.course_code,
    c.course_name,
    cd.department_name AS course_department
FROM students s
JOIN departments sd ON s.department_id = sd.department_id
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
JOIN departments cd ON c.department_id = cd.department_id
WHERE s.department_id != c.department_id
ORDER BY s.last_name, s.first_name;

-- 6. Course enrollment summary with department info
SELECT
    d.department_name,
    c.course_code,
    c.course_name,
    c.credits,
    c.max_capacity,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'enrolled') AS current_enrolled,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed') AS completed,
    COUNT(e.enrollment_id) FILTER (WHERE e.status IN ('dropped', 'withdrawn')) AS dropped_withdrawn,
    c.max_capacity - COUNT(e.enrollment_id) FILTER (WHERE e.status = 'enrolled') AS available_seats
FROM courses c
JOIN departments d ON c.department_id = d.department_id
LEFT JOIN enrollments e ON c.course_id = e.course_id
GROUP BY d.department_name, c.course_id, c.course_code, c.course_name, c.credits, c.max_capacity
ORDER BY d.department_name, c.course_code;

-- ============================================
-- DATA QUALITY QUERIES (Duplicates & Invalid Entries)
-- ============================================

-- 7. Find duplicate student emails
SELECT
    student_email,
    COUNT(*) AS occurrence_count
FROM students
GROUP BY student_email
HAVING COUNT(*) > 1;

-- 8. Students with invalid or missing data
SELECT
    student_id,
    student_email,
    first_name,
    last_name,
    year_level,
    department_id,
    CASE
        WHEN student_email IS NULL OR student_email = '' THEN 'Missing email'
        WHEN first_name IS NULL OR first_name = '' THEN 'Missing first name'
        WHEN last_name IS NULL OR last_name = '' THEN 'Missing last name'
        WHEN year_level IS NULL THEN 'Missing year level'
        WHEN year_level NOT BETWEEN 1 AND 4 THEN 'Invalid year level'
        WHEN department_id IS NULL THEN 'No department assigned'
        ELSE 'Valid'
    END AS validation_status
FROM students
WHERE
    student_email IS NULL OR student_email = ''
    OR first_name IS NULL OR first_name = ''
    OR last_name IS NULL OR last_name = ''
    OR year_level IS NULL
    OR year_level NOT BETWEEN 1 AND 4
    OR department_id IS NULL;

-- 9. Enrollments with missing or invalid grades (completed courses)
SELECT
    s.first_name || ' ' || s.last_name AS student_name,
    c.course_code,
    e.enrollment_date,
    e.status,
    e.grade,
    e.grade_points,
    CASE
        WHEN e.status = 'completed' AND e.grade IS NULL THEN 'Missing grade'
        WHEN e.status = 'completed' AND e.grade_points IS NULL THEN 'Missing grade points'
        WHEN e.grade_points IS NOT NULL AND (e.grade_points < 0 OR e.grade_points > 4) THEN 'Invalid GPA'
        ELSE 'Valid'
    END AS validation_status
FROM enrollments e
JOIN students s ON e.student_id = s.student_id
JOIN courses c ON e.course_id = c.course_id
WHERE
    (e.status = 'completed' AND (e.grade IS NULL OR e.grade_points IS NULL))
    OR (e.grade_points IS NOT NULL AND (e.grade_points < 0 OR e.grade_points > 4));

-- ============================================
-- REPORT QUERIES
-- ============================================

-- 10. Department performance report
SELECT
    d.department_name,
    d.department_head,
    COUNT(DISTINCT s.student_id) AS total_students,
    COUNT(DISTINCT c.course_id) AS total_courses,
    COUNT(DISTINCT e.enrollment_id) AS total_enrollments,
    ROUND(AVG(e.grade_points) FILTER (WHERE e.status = 'completed'), 2) AS avg_department_gpa,
    ROUND(AVG(e.attendance_percentage), 2) AS avg_attendance
FROM departments d
LEFT JOIN students s ON d.department_id = s.department_id
LEFT JOIN courses c ON d.department_id = c.department_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
GROUP BY d.department_id, d.department_name, d.department_head
ORDER BY total_students DESC;

-- 11. Top performing students (by GPA)
SELECT
    s.first_name || ' ' || s.last_name AS student_name,
    s.student_email,
    d.department_name,
    s.year_level,
    COUNT(e.enrollment_id) AS courses_completed,
    ROUND(AVG(e.grade_points), 3) AS cumulative_gpa,
    SUM(c.credits) AS total_credits_earned
FROM students s
JOIN departments d ON s.department_id = d.department_id
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
WHERE e.status = 'completed' AND e.grade_points IS NOT NULL
GROUP BY s.student_id, s.first_name, s.last_name, s.student_email, d.department_name, s.year_level
HAVING COUNT(e.enrollment_id) >= 2  -- At least 2 completed courses
ORDER BY cumulative_gpa DESC, courses_completed DESC
LIMIT 10;

-- 12. Courses with lowest pass rates
SELECT
    c.course_code,
    c.course_name,
    d.department_name,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed') AS total_completed,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed' AND e.grade NOT IN ('F', 'W', 'I')) AS passed,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed' AND e.grade IN ('F', 'W', 'I')) AS failed_or_withdrawn,
    ROUND(
        100.0 * COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed' AND e.grade NOT IN ('F', 'W', 'I')) /
        NULLIF(COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed'), 0),
        2
    ) AS pass_rate_percentage
FROM courses c
JOIN departments d ON c.department_id = d.department_id
LEFT JOIN enrollments e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name, d.department_name
HAVING COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed') > 0
ORDER BY pass_rate_percentage ASC;

-- 13. Student enrollment summary
SELECT
    s.first_name || ' ' || s.last_name AS student_name,
    s.enrollment_status AS student_status,
    COUNT(e.enrollment_id) AS total_courses,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'enrolled') AS currently_enrolled,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed') AS completed,
    COUNT(e.enrollment_id) FILTER (WHERE e.status IN ('dropped', 'withdrawn')) AS dropped,
    COALESCE(SUM(c.credits) FILTER (WHERE e.status = 'completed'), 0) AS credits_earned
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id
LEFT JOIN courses c ON e.course_id = c.course_id
GROUP BY s.student_id, s.first_name, s.last_name, s.enrollment_status
ORDER BY credits_earned DESC;

-- ============================================
-- ADVANCED ANALYTICS
-- ============================================

-- 14. Semester-wise enrollment trends
SELECT
    c.semester,
    COUNT(DISTINCT e.student_id) AS unique_students,
    COUNT(e.enrollment_id) AS total_enrollments,
    ROUND(AVG(e.grade_points) FILTER (WHERE e.status = 'completed'), 2) AS avg_gpa
FROM enrollments e
JOIN courses c ON e.course_id = c.course_id
GROUP BY c.semester
ORDER BY
    CASE c.semester
        WHEN 'Fall' THEN 1
        WHEN 'Spring' THEN 2
        WHEN 'Summer' THEN 3
    END;

-- 15. Student workload analysis (credits per student)
SELECT
    s.first_name || ' ' || s.last_name AS student_name,
    s.year_level,
    SUM(c.credits) FILTER (WHERE e.status = 'enrolled') AS current_credits,
    SUM(c.credits) FILTER (WHERE e.status = 'completed') AS completed_credits,
    COUNT(c.course_id) FILTER (WHERE e.status = 'enrolled') AS current_courses,
    CASE
        WHEN SUM(c.credits) FILTER (WHERE e.status = 'enrolled') > 18 THEN 'Overloaded'
        WHEN SUM(c.credits) FILTER (WHERE e.status = 'enrolled') >= 12 THEN 'Full-time'
        WHEN SUM(c.credits) FILTER (WHERE e.status = 'enrolled') >= 6 THEN 'Part-time'
        ELSE 'Light load'
    END AS workload_status
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
WHERE s.enrollment_status = 'active'
GROUP BY s.student_id, s.first_name, s.last_name, s.year_level
ORDER BY current_credits DESC;

-- ============================================
-- QUERY OPTIMIZATION: EXPLAIN ANALYZE EXAMPLES
-- ============================================

-- Run these with EXPLAIN ANALYZE to see query plans:

-- Example 1: Uses idx_enrollments_student index
-- EXPLAIN ANALYZE
-- SELECT * FROM enrollments WHERE student_id = 1;

-- Example 2: Uses idx_students_department index
-- EXPLAIN ANALYZE
-- SELECT s.*, d.department_name
-- FROM students s
-- JOIN departments d ON s.department_id = d.department_id
-- WHERE d.department_id = 1;

-- Example 3: Composite index usage
-- EXPLAIN ANALYZE
-- SELECT * FROM enrollments
-- WHERE student_id = 1 AND status = 'completed';
