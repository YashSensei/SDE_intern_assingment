"""
Simple REST API for Student Registration
Provides endpoint for Google App Script auto-registration workflow
"""

import os
import re
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import shared configuration (handle both module and direct execution)
try:
    from etl.config import DEPARTMENT_MAPPING, STATUS_MAPPING, API_CONFIG
except ModuleNotFoundError:
    from config import DEPARTMENT_MAPPING, STATUS_MAPPING, API_CONFIG

app = Flask(__name__)
CORS(app)  # Enable CORS for Google App Script

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', 5432)
    )

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def normalize_department(dept):
    """Normalize department name"""
    if not dept:
        return None
    return DEPARTMENT_MAPPING.get(dept.lower(), dept)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/register', methods=['POST'])
def register_student():
    """
    Register a new student
    Expected JSON payload:
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
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('email'):
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        if not validate_email(data['email']):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400

        if not data.get('first_name'):
            return jsonify({'success': False, 'message': 'First name is required'}), 400

        if not data.get('last_name'):
            return jsonify({'success': False, 'message': 'Last name is required'}), 400

        # Normalize data
        email = data['email'].lower().strip()
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        year_level = data.get('year_level', 1)
        department = normalize_department(data.get('department'))
        status = data.get('status', 'active').lower()
        phone = data.get('phone')
        dob = data.get('dob')

        # Validate year level
        if year_level and (year_level < 1 or year_level > 4):
            return jsonify({'success': False, 'message': 'Year level must be 1-4'}), 400

        # Validate status
        if status not in STATUS_MAPPING:
            status = 'active'

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Get department ID
            dept_id = None
            if department:
                cursor.execute(
                    "SELECT department_id FROM departments WHERE department_name = %s",
                    (department,)
                )
                result = cursor.fetchone()
                dept_id = result[0] if result else None

            # Check if student already exists
            cursor.execute(
                "SELECT student_id FROM students WHERE student_email = %s",
                (email,)
            )
            existing = cursor.fetchone()

            if existing:
                # Update existing student
                cursor.execute("""
                    UPDATE students SET
                        first_name = %s,
                        last_name = %s,
                        year_level = %s,
                        department_id = %s,
                        enrollment_status = %s,
                        phone_number = %s,
                        date_of_birth = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE student_email = %s
                    RETURNING student_id
                """, (first_name, last_name, year_level, dept_id, status, phone, dob, email))

                student_id = cursor.fetchone()[0]
                conn.commit()

                return jsonify({
                    'success': True,
                    'message': 'Student updated successfully',
                    'student_id': student_id,
                    'action': 'updated'
                }), 200

            else:
                # Insert new student
                cursor.execute("""
                    INSERT INTO students (
                        student_email, first_name, last_name, year_level,
                        department_id, enrollment_status, phone_number, date_of_birth
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING student_id
                """, (email, first_name, last_name, year_level, dept_id, status, phone, dob))

                student_id = cursor.fetchone()[0]
                conn.commit()

                return jsonify({
                    'success': True,
                    'message': 'Student registered successfully',
                    'student_id': student_id,
                    'action': 'created'
                }), 201

        finally:
            cursor.close()
            conn.close()

    except psycopg2.IntegrityError as e:
        return jsonify({'success': False, 'message': f'Database constraint error: {str(e)}'}), 409
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/students', methods=['GET'])
def list_students():
    """List all students"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                s.student_id,
                s.student_email,
                s.first_name,
                s.last_name,
                s.year_level,
                d.department_name,
                s.enrollment_status
            FROM students s
            LEFT JOIN departments d ON s.department_id = d.department_id
            ORDER BY s.student_id
        """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        students = []
        for row in rows:
            students.append({
                'student_id': row[0],
                'email': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'year_level': row[4],
                'department': row[5],
                'status': row[6]
            })

        return jsonify({'success': True, 'students': students, 'count': len(students)})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get a specific student"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                s.student_id,
                s.student_email,
                s.first_name,
                s.last_name,
                s.year_level,
                d.department_name,
                s.enrollment_status,
                s.phone_number,
                s.date_of_birth
            FROM students s
            LEFT JOIN departments d ON s.department_id = d.department_id
            WHERE s.student_id = %s
        """, (student_id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return jsonify({'success': False, 'message': 'Student not found'}), 404

        return jsonify({
            'success': True,
            'student': {
                'student_id': row[0],
                'email': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'year_level': row[4],
                'department': row[5],
                'status': row[6],
                'phone': row[7],
                'dob': row[8].isoformat() if row[8] else None
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )
