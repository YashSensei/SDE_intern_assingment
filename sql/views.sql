-- ============================================
-- SDE Intern Assignment - Database Views
-- Task 5: SQL Development & Optimization
-- ============================================

-- ============================================
-- REGULAR VIEWS
-- ============================================

-- 1. Student Overview View
-- Combines student info with department and enrollment stats
DROP VIEW IF EXISTS vw_student_overview CASCADE;
CREATE VIEW vw_student_overview AS
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS full_name,
    s.student_email,
    s.year_level,
    d.department_name,
    s.enrollment_status,
    s.phone_number,
    s.date_of_birth,
    COUNT(e.enrollment_id) AS total_enrollments,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'enrolled') AS current_courses,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed') AS completed_courses,
    COALESCE(ROUND(AVG(e.grade_points) FILTER (WHERE e.status = 'completed'), 2), 0) AS gpa,
    COALESCE(SUM(c.credits) FILTER (WHERE e.status = 'completed'), 0) AS credits_earned
FROM students s
LEFT JOIN departments d ON s.department_id = d.department_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
LEFT JOIN courses c ON e.course_id = c.course_id
GROUP BY
    s.student_id, s.first_name, s.last_name, s.student_email,
    s.year_level, d.department_name, s.enrollment_status,
    s.phone_number, s.date_of_birth;

COMMENT ON VIEW vw_student_overview IS 'Comprehensive student view with enrollment statistics and GPA';

-- 2. Course Enrollment Summary View
DROP VIEW IF EXISTS vw_course_enrollment_summary CASCADE;
CREATE VIEW vw_course_enrollment_summary AS
SELECT
    c.course_id,
    c.course_code,
    c.course_name,
    d.department_name,
    c.credits,
    c.semester,
    c.max_capacity,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'enrolled') AS current_enrolled,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed') AS total_completed,
    COUNT(e.enrollment_id) FILTER (WHERE e.status IN ('dropped', 'withdrawn')) AS total_dropped,
    c.max_capacity - COUNT(e.enrollment_id) FILTER (WHERE e.status = 'enrolled') AS available_seats,
    ROUND(AVG(e.grade_points) FILTER (WHERE e.status = 'completed'), 2) AS avg_grade,
    ROUND(AVG(e.attendance_percentage), 2) AS avg_attendance,
    ROUND(
        100.0 * COUNT(e.enrollment_id) FILTER (WHERE e.status = 'enrolled') / NULLIF(c.max_capacity, 0),
        1
    ) AS capacity_percentage
FROM courses c
JOIN departments d ON c.department_id = d.department_id
LEFT JOIN enrollments e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name, d.department_name,
         c.credits, c.semester, c.max_capacity;

COMMENT ON VIEW vw_course_enrollment_summary IS 'Course enrollment statistics with capacity tracking';

-- 3. Department Statistics View
DROP VIEW IF EXISTS vw_department_stats CASCADE;
CREATE VIEW vw_department_stats AS
SELECT
    d.department_id,
    d.department_name,
    d.department_head,
    d.building,
    COUNT(DISTINCT s.student_id) AS total_students,
    COUNT(DISTINCT s.student_id) FILTER (WHERE s.enrollment_status = 'active') AS active_students,
    COUNT(DISTINCT c.course_id) AS total_courses,
    SUM(c.credits) AS total_credit_hours_offered,
    COUNT(DISTINCT e.enrollment_id) AS total_enrollments,
    ROUND(AVG(e.grade_points) FILTER (WHERE e.status = 'completed'), 2) AS dept_avg_gpa,
    ROUND(AVG(e.attendance_percentage), 2) AS dept_avg_attendance
FROM departments d
LEFT JOIN students s ON d.department_id = s.department_id
LEFT JOIN courses c ON d.department_id = c.department_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
GROUP BY d.department_id, d.department_name, d.department_head, d.building;

COMMENT ON VIEW vw_department_stats IS 'Department-level statistics for administrative reporting';

-- 4. Student Transcript View
DROP VIEW IF EXISTS vw_student_transcript CASCADE;
CREATE VIEW vw_student_transcript AS
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    s.student_email,
    c.course_code,
    c.course_name,
    c.credits,
    cd.department_name AS course_department,
    e.enrollment_date,
    e.grade,
    e.grade_points,
    e.attendance_percentage,
    e.status AS enrollment_status,
    CASE
        WHEN e.status = 'completed' AND e.grade_points >= 2.0 THEN 'Pass'
        WHEN e.status = 'completed' AND e.grade_points < 2.0 THEN 'Fail'
        WHEN e.status = 'enrolled' THEN 'In Progress'
        ELSE 'Not Counted'
    END AS grade_status
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
JOIN departments cd ON c.department_id = cd.department_id
ORDER BY s.student_id, e.enrollment_date;

COMMENT ON VIEW vw_student_transcript IS 'Detailed transcript view for each student';

-- 5. Active Enrollments View (Current courses)
DROP VIEW IF EXISTS vw_active_enrollments CASCADE;
CREATE VIEW vw_active_enrollments AS
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    s.student_email,
    sd.department_name AS student_department,
    c.course_code,
    c.course_name,
    cd.department_name AS course_department,
    c.credits,
    c.semester,
    e.enrollment_date,
    e.attendance_percentage
FROM students s
JOIN departments sd ON s.department_id = sd.department_id
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
JOIN departments cd ON c.department_id = cd.department_id
WHERE e.status = 'enrolled' AND s.enrollment_status = 'active';

COMMENT ON VIEW vw_active_enrollments IS 'Currently active course enrollments';

-- 6. At-Risk Students View (Low GPA or attendance)
DROP VIEW IF EXISTS vw_at_risk_students CASCADE;
CREATE VIEW vw_at_risk_students AS
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    s.student_email,
    d.department_name,
    s.year_level,
    ROUND(AVG(e.grade_points) FILTER (WHERE e.status = 'completed'), 2) AS cumulative_gpa,
    ROUND(AVG(e.attendance_percentage), 2) AS avg_attendance,
    COUNT(e.enrollment_id) FILTER (WHERE e.grade IN ('D', 'F')) AS failing_grades,
    CASE
        WHEN AVG(e.grade_points) FILTER (WHERE e.status = 'completed') < 2.0 THEN 'Academic Probation'
        WHEN AVG(e.attendance_percentage) < 70 THEN 'Attendance Warning'
        WHEN COUNT(e.enrollment_id) FILTER (WHERE e.grade IN ('D', 'F')) >= 2 THEN 'Multiple Failures'
        ELSE 'Monitor'
    END AS risk_category
FROM students s
JOIN departments d ON s.department_id = d.department_id
JOIN enrollments e ON s.student_id = e.student_id
WHERE s.enrollment_status = 'active'
GROUP BY s.student_id, s.first_name, s.last_name, s.student_email, d.department_name, s.year_level
HAVING
    AVG(e.grade_points) FILTER (WHERE e.status = 'completed') < 2.5
    OR AVG(e.attendance_percentage) < 75
    OR COUNT(e.enrollment_id) FILTER (WHERE e.grade IN ('D', 'F')) >= 1;

COMMENT ON VIEW vw_at_risk_students IS 'Students requiring academic intervention';

-- ============================================
-- MATERIALIZED VIEWS (For Dashboard Performance)
-- ============================================

-- 7. Department Dashboard (Materialized)
DROP MATERIALIZED VIEW IF EXISTS mv_department_dashboard CASCADE;
CREATE MATERIALIZED VIEW mv_department_dashboard AS
SELECT
    d.department_id,
    d.department_name,
    d.department_head,
    COUNT(DISTINCT s.student_id) AS total_students,
    COUNT(DISTINCT c.course_id) AS total_courses,
    COUNT(DISTINCT e.enrollment_id) AS total_enrollments,
    ROUND(AVG(e.grade_points) FILTER (WHERE e.status = 'completed'), 2) AS avg_gpa,
    COUNT(DISTINCT s.student_id) FILTER (WHERE s.year_level = 1) AS freshmen,
    COUNT(DISTINCT s.student_id) FILTER (WHERE s.year_level = 2) AS sophomores,
    COUNT(DISTINCT s.student_id) FILTER (WHERE s.year_level = 3) AS juniors,
    COUNT(DISTINCT s.student_id) FILTER (WHERE s.year_level = 4) AS seniors,
    CURRENT_TIMESTAMP AS last_refreshed
FROM departments d
LEFT JOIN students s ON d.department_id = s.department_id AND s.enrollment_status = 'active'
LEFT JOIN courses c ON d.department_id = c.department_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
GROUP BY d.department_id, d.department_name, d.department_head;

CREATE UNIQUE INDEX idx_mv_dept_dashboard ON mv_department_dashboard(department_id);

COMMENT ON MATERIALIZED VIEW mv_department_dashboard IS 'Pre-computed department statistics for dashboard';

-- 8. Course Performance Dashboard (Materialized)
DROP MATERIALIZED VIEW IF EXISTS mv_course_performance CASCADE;
CREATE MATERIALIZED VIEW mv_course_performance AS
SELECT
    c.course_id,
    c.course_code,
    c.course_name,
    d.department_name,
    c.credits,
    c.semester,
    COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed') AS completions,
    ROUND(AVG(e.grade_points) FILTER (WHERE e.status = 'completed'), 2) AS avg_grade,
    ROUND(
        100.0 * COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed' AND e.grade_points >= 2.0) /
        NULLIF(COUNT(e.enrollment_id) FILTER (WHERE e.status = 'completed'), 0),
        1
    ) AS pass_rate,
    ROUND(AVG(e.attendance_percentage), 1) AS avg_attendance,
    CURRENT_TIMESTAMP AS last_refreshed
FROM courses c
JOIN departments d ON c.department_id = d.department_id
LEFT JOIN enrollments e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name, d.department_name, c.credits, c.semester;

CREATE UNIQUE INDEX idx_mv_course_perf ON mv_course_performance(course_id);

COMMENT ON MATERIALIZED VIEW mv_course_performance IS 'Pre-computed course performance metrics';

-- ============================================
-- REFRESH FUNCTION FOR MATERIALIZED VIEWS
-- ============================================

CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_dashboard;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_course_performance;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_all_materialized_views() IS 'Refresh all materialized views (run periodically)';

-- ============================================
-- VERIFICATION
-- ============================================

-- List all views created
SELECT
    table_name AS view_name,
    CASE table_type
        WHEN 'VIEW' THEN 'Regular View'
        WHEN 'BASE TABLE' THEN 'Materialized View'
    END AS view_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND (table_name LIKE 'vw_%' OR table_name LIKE 'mv_%')
ORDER BY table_name;
