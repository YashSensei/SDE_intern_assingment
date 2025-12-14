-- Drop all tables in correct order (respecting foreign key constraints)
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- Confirmation message
SELECT 'Database reset complete - all tables dropped' AS status;
