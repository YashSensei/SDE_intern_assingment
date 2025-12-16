"""
ETL Configuration Settings
Centralized configuration for the ETL pipeline
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', 5432)
}

# Google Sheets Configuration
GOOGLE_CONFIG = {
    'credentials_file': os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json'),
    'sheet_id': os.getenv('GOOGLE_SHEET_ID'),
    'sheet_name': os.getenv('GOOGLE_SHEET_NAME', 'Sheet1'),
    'scopes': ['https://www.googleapis.com/auth/spreadsheets.readonly']
}

# Data Transformation Rules
DEPARTMENT_MAPPING = {
    'cs': 'Computer Science',
    'compsci': 'Computer Science',
    'computer science': 'Computer Science',
    'math': 'Mathematics',
    'mathematics': 'Mathematics',
    'physics': 'Physics',
    'business': 'Business Administration',
    'business administration': 'Business Administration',
    'ee': 'Electrical Engineering',
    'electrical engineering': 'Electrical Engineering'
}

STATUS_MAPPING = {
    'active': 'active',
    'inactive': 'inactive',
    'graduated': 'graduated',
    'suspended': 'suspended'
}

# Validation Rules
VALIDATION_RULES = {
    'year_min': 1,
    'year_max': 4,
    'gpa_min': 0.0,
    'gpa_max': 4.0,
    'email_pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'
}

# Logging Configuration
LOG_CONFIG = {
    'log_dir': 'etl/logs',
    'log_format': '%(asctime)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}
