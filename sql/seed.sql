-- ============================================
-- SDE Intern Assignment - Seed Data
-- Purpose: Sample data for testing and demonstration
-- ============================================

-- Clear existing data
TRUNCATE TABLE enrollments, courses, students, departments RESTART IDENTITY CASCADE;

-- ============================================
-- DEPARTMENTS
-- ============================================
INSERT INTO departments (department_name, department_head, building) VALUES
('Computer Science', 'Dr. Alan Turing', 'Tech Center'),
('Mathematics', 'Dr. Emmy Noether', 'Science Hall'),
('Physics', 'Dr. Marie Curie', 'Research Lab'),
('Business Administration', 'Dr. Peter Drucker', 'Business Building'),
('Electrical Engineering', 'Dr. Nikola Tesla', 'Engineering Wing');

-- ============================================
-- STUDENTS
-- ============================================
INSERT INTO students (student_email, first_name, last_name, year_level, department_id, enrollment_status, phone_number, date_of_birth) VALUES
-- Computer Science Students
('john.doe@university.edu', 'John', 'Doe', 3, 1, 'active', '555-0101', '2003-05-15'),
('jane.smith@university.edu', 'Jane', 'Smith', 2, 1, 'active', '555-0102', '2004-08-22'),
('alice.johnson@university.edu', 'Alice', 'Johnson', 4, 1, 'active', '555-0103', '2002-11-30'),
('bob.williams@university.edu', 'Bob', 'Williams', 1, 1, 'active', '555-0104', '2005-02-14'),

-- Mathematics Students
('charlie.brown@university.edu', 'Charlie', 'Brown', 3, 2, 'active', '555-0201', '2003-07-10'),
('diana.prince@university.edu', 'Diana', 'Prince', 2, 2, 'active', '555-0202', '2004-03-25'),
('eve.davis@university.edu', 'Eve', 'Davis', 4, 2, 'active', '555-0203', '2002-09-18'),

-- Physics Students
('frank.miller@university.edu', 'Frank', 'Miller', 2, 3, 'active', '555-0301', '2004-12-05'),
('grace.lee@university.edu', 'Grace', 'Lee', 3, 3, 'active', '555-0302', '2003-01-20'),

-- Business Students
('henry.garcia@university.edu', 'Henry', 'Garcia', 1, 4, 'active', '555-0401', '2005-06-08'),
('iris.martinez@university.edu', 'Iris', 'Martinez', 2, 4, 'active', '555-0402', '2004-04-17'),

-- Engineering Students
('jack.anderson@university.edu', 'Jack', 'Anderson', 4, 5, 'active', '555-0501', '2002-10-12'),
('kate.thomas@university.edu', 'Kate', 'Thomas', 3, 5, 'active', '555-0502', '2003-08-28'),

-- Graduated Students
('legacy.student@university.edu', 'Legacy', 'Student', 4, 1, 'graduated', '555-0999', '2001-01-01'),

-- Inactive Student
('inactive.user@university.edu', 'Inactive', 'User', 2, 2, 'inactive', '555-0998', '2004-05-05');

-- ============================================
-- COURSES
-- ============================================
INSERT INTO courses (course_code, course_name, department_id, credits, max_capacity, semester, course_description) VALUES
-- Computer Science Courses
('CS101', 'Introduction to Programming', 1, 3, 100, 'Fall', 'Fundamentals of programming using Python'),
('CS201', 'Data Structures', 1, 4, 80, 'Spring', 'Advanced data structures and algorithms'),
('CS301', 'Database Systems', 1, 3, 60, 'Fall', 'Relational databases, SQL, and NoSQL systems'),
('CS401', 'Machine Learning', 1, 4, 50, 'Spring', 'Introduction to ML algorithms and applications'),
('CS202', 'Web Development', 1, 3, 70, 'Summer', 'Full-stack web development with modern frameworks'),

-- Mathematics Courses
('MATH101', 'Calculus I', 2, 4, 120, 'Fall', 'Differential calculus and applications'),
('MATH201', 'Linear Algebra', 2, 3, 90, 'Spring', 'Matrices, vector spaces, and linear transformations'),
('MATH301', 'Probability Theory', 2, 3, 60, 'Fall', 'Probability distributions and statistical inference'),

-- Physics Courses
('PHYS101', 'Physics I', 3, 4, 100, 'Fall', 'Mechanics and thermodynamics'),
('PHYS201', 'Physics II', 3, 4, 80, 'Spring', 'Electricity, magnetism, and optics'),

-- Business Courses
('BUS101', 'Introduction to Business', 4, 3, 150, 'Fall', 'Fundamentals of business operations'),
('BUS201', 'Marketing Principles', 4, 3, 80, 'Spring', 'Marketing strategies and consumer behavior'),
('BUS301', 'Financial Management', 4, 4, 60, 'Fall', 'Corporate finance and investment analysis'),

-- Engineering Courses
('EE101', 'Circuit Analysis', 5, 4, 70, 'Fall', 'Basic electrical circuit theory'),
('EE201', 'Digital Logic Design', 5, 3, 60, 'Spring', 'Boolean algebra and digital systems'),
('EE301', 'Signals and Systems', 5, 4, 50, 'Fall', 'Signal processing and system analysis');

-- ============================================
-- ENROLLMENTS
-- ============================================
INSERT INTO enrollments (student_id, course_id, enrollment_date, grade, grade_points, attendance_percentage, status) VALUES
-- John Doe (CS Year 3) - Completed courses
(1, 1, '2023-08-20', 'A', 4.00, 95.00, 'completed'),
(1, 2, '2024-01-15', 'A-', 3.70, 92.00, 'completed'),
(1, 3, '2024-08-20', NULL, NULL, 88.50, 'enrolled'),
(1, 6, '2023-08-20', 'B+', 3.30, 85.00, 'completed'),

-- Jane Smith (CS Year 2) - Mix of enrolled and completed
(2, 1, '2024-01-15', 'A+', 4.00, 98.00, 'completed'),
(2, 2, '2024-08-20', NULL, NULL, 91.00, 'enrolled'),
(2, 5, '2024-08-20', NULL, NULL, 87.00, 'enrolled'),

-- Alice Johnson (CS Year 4) - Senior with advanced courses
(3, 3, '2024-08-20', NULL, NULL, 94.00, 'enrolled'),
(3, 4, '2024-01-15', NULL, NULL, 90.00, 'enrolled'),
(3, 2, '2023-08-20', 'A', 4.00, 96.00, 'completed'),

-- Bob Williams (CS Year 1) - Freshman
(4, 1, '2024-08-20', NULL, NULL, 78.00, 'enrolled'),

-- Charlie Brown (Math Year 3)
(5, 6, '2023-08-20', 'A-', 3.70, 93.00, 'completed'),
(5, 7, '2024-01-15', 'B+', 3.30, 88.00, 'completed'),
(5, 8, '2024-08-20', NULL, NULL, 91.00, 'enrolled'),

-- Diana Prince (Math Year 2)
(6, 6, '2024-01-15', 'A', 4.00, 97.00, 'completed'),
(6, 7, '2024-08-20', NULL, NULL, 89.00, 'enrolled'),

-- Eve Davis (Math Year 4)
(7, 7, '2023-08-20', 'A+', 4.00, 99.00, 'completed'),
(7, 8, '2024-01-15', 'A', 4.00, 95.00, 'completed'),

-- Frank Miller (Physics Year 2)
(8, 9, '2024-01-15', 'B', 3.00, 86.00, 'completed'),
(8, 10, '2024-08-20', NULL, NULL, 84.00, 'enrolled'),

-- Grace Lee (Physics Year 3)
(9, 9, '2023-08-20', 'A-', 3.70, 92.00, 'completed'),
(9, 10, '2024-01-15', 'A', 4.00, 94.00, 'completed'),

-- Henry Garcia (Business Year 1)
(10, 11, '2024-08-20', NULL, NULL, 82.00, 'enrolled'),

-- Iris Martinez (Business Year 2)
(11, 11, '2024-01-15', 'B+', 3.30, 87.00, 'completed'),
(11, 12, '2024-08-20', NULL, NULL, 90.00, 'enrolled'),

-- Jack Anderson (EE Year 4)
(12, 14, '2023-08-20', 'A', 4.00, 93.00, 'completed'),
(12, 15, '2024-01-15', 'A-', 3.70, 91.00, 'completed'),
(12, 16, '2024-08-20', NULL, NULL, 89.00, 'enrolled'),

-- Kate Thomas (EE Year 3)
(13, 14, '2024-01-15', 'B+', 3.30, 85.00, 'completed'),
(13, 15, '2024-08-20', NULL, NULL, 88.00, 'enrolled'),

-- Some dropped/withdrawn enrollments
(2, 6, '2024-01-15', 'W', NULL, 45.00, 'withdrawn'),
(4, 6, '2024-01-15', NULL, NULL, 30.00, 'dropped');

-- ============================================
-- Verification Queries
-- ============================================

-- Count records
SELECT 'Departments' AS table_name, COUNT(*) AS record_count FROM departments
UNION ALL
SELECT 'Students', COUNT(*) FROM students
UNION ALL
SELECT 'Courses', COUNT(*) FROM courses
UNION ALL
SELECT 'Enrollments', COUNT(*) FROM enrollments;

-- Display sample data
SELECT 
    s.first_name || ' ' || s.last_name AS student_name,
    d.department_name,
    s.year_level,
    s.enrollment_status,
    COUNT(e.enrollment_id) AS total_enrollments,
    AVG(e.grade_points) AS avg_gpa
FROM students s
LEFT JOIN departments d ON s.department_id = d.department_id
LEFT JOIN enrollments e ON s.student_id = e.student_id AND e.status = 'completed'
GROUP BY s.student_id, s.first_name, s.last_name, d.department_name, s.year_level, s.enrollment_status
ORDER BY s.student_id
LIMIT 10;
