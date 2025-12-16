"""
ETL Pipeline - Google Sheets to NeonDB Migration
Extracts data from Google Sheets, transforms/validates, and loads into PostgreSQL
"""

import os
import sys
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# ============================================
# LOGGING SETUP
# ============================================

def setup_logging():
    """Configure logging with both file and console output"""
    log_dir = 'etl/logs'
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'etl_run_{timestamp}.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__), log_file

logger, log_file = setup_logging()

# ============================================
# CONFIGURATION
# ============================================

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

# ============================================
# EXTRACT PHASE
# ============================================

class DataExtractor:
    """Handles data extraction from various sources"""

    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    def extract_from_google_sheets(self, sheet_id: str, range_name: str = 'Sheet1') -> pd.DataFrame:
        """Extract data from Google Sheets"""
        logger.info(f"Extracting data from Google Sheets: {sheet_id}")

        try:
            creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

            if not os.path.exists(creds_file):
                raise FileNotFoundError(f"Credentials file not found: {creds_file}")

            credentials = service_account.Credentials.from_service_account_file(
                creds_file, scopes=self.scopes
            )

            service = build('sheets', 'v4', credentials=credentials)
            sheet = service.spreadsheets()

            result = sheet.values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])

            if not values:
                logger.warning("No data found in Google Sheet")
                return pd.DataFrame()

            # Convert to DataFrame
            headers = values[0]
            data = values[1:]

            # Handle rows with fewer columns than headers
            normalized_data = []
            for row in data:
                normalized_row = row + [''] * (len(headers) - len(row))
                normalized_data.append(normalized_row[:len(headers)])

            df = pd.DataFrame(normalized_data, columns=headers)

            logger.info(f"Extracted {len(df)} records from Google Sheets")
            return df

        except Exception as e:
            logger.error(f"Failed to extract from Google Sheets: {e}")
            raise

    def extract_from_csv(self, filepath: str) -> pd.DataFrame:
        """Extract data from CSV file (fallback/testing)"""
        logger.info(f"Extracting data from CSV: {filepath}")

        try:
            df = pd.read_csv(filepath, dtype=str)
            df = df.fillna('')
            logger.info(f"Extracted {len(df)} records from CSV")
            return df
        except Exception as e:
            logger.error(f"Failed to extract from CSV: {e}")
            raise

# ============================================
# TRANSFORM PHASE
# ============================================

class DataTransformer:
    """Handles data validation, cleaning, and transformation"""

    def __init__(self):
        self.validation_errors = []
        self.transformation_log = []

    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Main transformation pipeline"""
        logger.info("Starting data transformation...")

        original_count = len(df)

        # Step 1: Remove exact duplicates
        df = self._remove_duplicates(df)

        # Step 2: Clean and normalize columns
        df = self._normalize_columns(df)

        # Step 3: Validate and clean each field
        df = self._validate_and_clean(df)

        # Step 4: Map to target schema
        df = self._map_to_schema(df)

        # Generate transformation report
        report = {
            'original_count': original_count,
            'final_count': len(df),
            'duplicates_removed': original_count - len(df),
            'validation_errors': self.validation_errors,
            'transformations': self.transformation_log
        }

        logger.info(f"Transformation complete: {original_count} -> {len(df)} records")
        return df, report

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records based on Student ID"""
        initial_count = len(df)

        # Identify duplicates by Student ID
        if 'Student ID' in df.columns:
            duplicates = df[df.duplicated(subset=['Student ID'], keep='first')]
            if not duplicates.empty:
                for idx, row in duplicates.iterrows():
                    self.transformation_log.append({
                        'action': 'DUPLICATE_REMOVED',
                        'student_id': row.get('Student ID', 'N/A'),
                        'reason': 'Duplicate Student ID'
                    })

            df = df.drop_duplicates(subset=['Student ID'], keep='first')

        removed = initial_count - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate records")

        return df

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names and strip whitespace"""
        # Standardize column names
        column_mapping = {
            'Student ID': 'student_id',
            'Email': 'email',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Year': 'year_level',
            'Department': 'department',
            'Status': 'status',
            'Phone': 'phone',
            'DOB': 'date_of_birth',
            'GPA': 'gpa'
        }

        df = df.rename(columns=column_mapping)

        # Strip whitespace from all string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()

        return df

    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean each field"""

        # Clean emails
        if 'email' in df.columns:
            df['email'] = df['email'].apply(self._clean_email)

        # Clean and map departments
        if 'department' in df.columns:
            df['department'] = df['department'].apply(self._map_department)

        # Clean and map status
        if 'status' in df.columns:
            df['status'] = df['status'].apply(self._map_status)

        # Clean year level
        if 'year_level' in df.columns:
            df['year_level'] = df['year_level'].apply(self._clean_year)

        # Clean phone numbers
        if 'phone' in df.columns:
            df['phone'] = df['phone'].apply(self._clean_phone)

        # Clean dates
        if 'date_of_birth' in df.columns:
            df['date_of_birth'] = df['date_of_birth'].apply(self._clean_date)

        # Clean GPA
        if 'gpa' in df.columns:
            df['gpa'] = df['gpa'].apply(self._clean_gpa)

        return df

    def _clean_email(self, email: str) -> Optional[str]:
        """Validate and clean email address"""
        if not email or email == '' or email == 'nan':
            return None

        email = email.lower().strip()
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, email):
            self.validation_errors.append({
                'field': 'email',
                'value': email,
                'error': 'Invalid email format'
            })
            return None

        return email

    def _map_department(self, dept: str) -> Optional[str]:
        """Map department name variations to standard names"""
        if not dept or dept == '' or dept == 'nan':
            return None

        dept_lower = dept.lower().strip()

        if dept_lower in DEPARTMENT_MAPPING:
            mapped = DEPARTMENT_MAPPING[dept_lower]
            if mapped != dept:
                self.transformation_log.append({
                    'action': 'DEPARTMENT_NORMALIZED',
                    'original': dept,
                    'normalized': mapped
                })
            return mapped

        # Return original if no mapping found
        return dept

    def _map_status(self, status: str) -> str:
        """Map status variations to standard values"""
        if not status or status == '' or status == 'nan':
            return 'active'

        status_lower = status.lower().strip()

        if status_lower in STATUS_MAPPING:
            return STATUS_MAPPING[status_lower]

        return 'active'  # Default to active

    def _clean_year(self, year) -> Optional[int]:
        """Clean and validate year level"""
        if not year or year == '' or year == 'nan':
            return None

        try:
            year_int = int(float(year))
            if 1 <= year_int <= 4:
                return year_int
            else:
                self.validation_errors.append({
                    'field': 'year_level',
                    'value': year,
                    'error': f'Year {year_int} out of range (1-4)'
                })
                # Clamp to valid range
                return max(1, min(4, year_int))
        except (ValueError, TypeError):
            return None

    def _clean_phone(self, phone: str) -> Optional[str]:
        """Clean and standardize phone number"""
        if not phone or phone == '' or phone == 'nan':
            return None

        # Remove all non-digits
        digits = re.sub(r'\D', '', str(phone))

        if len(digits) == 10:
            # Format as XXX-XXX-XXXX
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 7:
            # Format as XXX-XXXX
            return f"{digits[:3]}-{digits[3:]}"

        return phone  # Return original if can't normalize

    def _clean_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats and standardize to YYYY-MM-DD"""
        if not date_str or date_str == '' or date_str == 'nan':
            return None

        date_formats = [
            '%Y-%m-%d',      # 2003-05-15
            '%m/%d/%Y',      # 05/15/2003
            '%m-%d-%Y',      # 05-15-2003
            '%d/%m/%Y',      # 15/05/2003
            '%d-%m-%Y',      # 15-05-2003
        ]

        for fmt in date_formats:
            try:
                parsed = datetime.strptime(date_str.strip(), fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue

        self.validation_errors.append({
            'field': 'date_of_birth',
            'value': date_str,
            'error': 'Unable to parse date'
        })
        return None

    def _clean_gpa(self, gpa) -> Optional[float]:
        """Clean and validate GPA"""
        if not gpa or gpa == '' or gpa == 'nan' or gpa == '##':
            return None

        try:
            gpa_float = float(gpa)
            if 0.0 <= gpa_float <= 4.0:
                return round(gpa_float, 2)
            else:
                self.validation_errors.append({
                    'field': 'gpa',
                    'value': gpa,
                    'error': f'GPA {gpa_float} out of range (0-4)'
                })
                return None
        except (ValueError, TypeError):
            return None

    def _map_to_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map transformed data to target database schema"""
        # Select and order columns for database
        schema_columns = [
            'student_id', 'email', 'first_name', 'last_name',
            'year_level', 'department', 'status', 'phone', 'date_of_birth'
        ]

        # Only keep columns that exist
        available_columns = [col for col in schema_columns if col in df.columns]

        return df[available_columns]

# ============================================
# LOAD PHASE
# ============================================

class DataLoader:
    """Handles loading data into PostgreSQL/NeonDB"""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT', 5432)
            )
            self.cursor = self.conn.cursor()
            logger.info("Connected to NeonDB successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")

    def load(self, df: pd.DataFrame) -> Dict:
        """Load transformed data into database"""
        logger.info("Starting data load to NeonDB...")

        load_stats = {
            'departments_inserted': 0,
            'students_inserted': 0,
            'students_updated': 0,
            'errors': []
        }

        try:
            # Step 1: Ensure departments exist
            self._load_departments(df, load_stats)

            # Step 2: Load students
            self._load_students(df, load_stats)

            # Commit transaction
            self.conn.commit()
            logger.info("Data load completed successfully")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Data load failed: {e}")
            load_stats['errors'].append(str(e))
            raise

        return load_stats

    def _load_departments(self, df: pd.DataFrame, stats: Dict):
        """Insert departments if they don't exist"""
        if 'department' not in df.columns:
            return

        departments = df['department'].dropna().unique()

        for dept in departments:
            if not dept:
                continue

            # Check if department exists
            self.cursor.execute(
                "SELECT department_id FROM departments WHERE department_name = %s",
                (dept,)
            )

            if not self.cursor.fetchone():
                # Insert new department
                self.cursor.execute(
                    """INSERT INTO departments (department_name)
                       VALUES (%s)
                       ON CONFLICT (department_name) DO NOTHING""",
                    (dept,)
                )
                stats['departments_inserted'] += 1
                logger.info(f"Inserted department: {dept}")

    def _load_students(self, df: pd.DataFrame, stats: Dict):
        """Insert or update students using upsert"""

        for _, row in df.iterrows():
            try:
                # Get department_id
                dept_id = None
                if row.get('department'):
                    self.cursor.execute(
                        "SELECT department_id FROM departments WHERE department_name = %s",
                        (row['department'],)
                    )
                    result = self.cursor.fetchone()
                    dept_id = result[0] if result else None

                # Check if student exists by email
                email = row.get('email')
                if not email:
                    logger.warning(f"Skipping student with no email: {row.get('first_name', 'Unknown')}")
                    continue

                self.cursor.execute(
                    "SELECT student_id FROM students WHERE student_email = %s",
                    (email,)
                )
                existing = self.cursor.fetchone()

                if existing:
                    # Update existing student
                    self.cursor.execute("""
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
                    """, (
                        row.get('first_name'),
                        row.get('last_name'),
                        row.get('year_level'),
                        dept_id,
                        row.get('status', 'active'),
                        row.get('phone'),
                        row.get('date_of_birth'),
                        email
                    ))
                    stats['students_updated'] += 1
                    logger.debug(f"Updated student: {email}")
                else:
                    # Insert new student
                    self.cursor.execute("""
                        INSERT INTO students (
                            student_email, first_name, last_name, year_level,
                            department_id, enrollment_status, phone_number, date_of_birth
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        email,
                        row.get('first_name'),
                        row.get('last_name'),
                        row.get('year_level'),
                        dept_id,
                        row.get('status', 'active'),
                        row.get('phone'),
                        row.get('date_of_birth')
                    ))
                    stats['students_inserted'] += 1
                    logger.debug(f"Inserted student: {email}")

            except Exception as e:
                logger.error(f"Error loading student {row.get('email', 'Unknown')}: {e}")
                stats['errors'].append(f"Student {row.get('email')}: {str(e)}")

# ============================================
# ETL ORCHESTRATOR
# ============================================

class ETLPipeline:
    """Main ETL orchestrator"""

    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()

    def run(self, source: str = 'sheets', source_path: str = None) -> Dict:
        """Execute the complete ETL pipeline"""

        logger.info("=" * 60)
        logger.info("ETL PIPELINE STARTED")
        logger.info("=" * 60)

        start_time = datetime.now()

        pipeline_report = {
            'start_time': start_time.isoformat(),
            'source': source,
            'extract': {},
            'transform': {},
            'load': {},
            'status': 'SUCCESS'
        }

        try:
            # EXTRACT
            logger.info("\n[PHASE 1/3] EXTRACT")
            logger.info("-" * 40)

            if source == 'sheets':
                sheet_id = os.getenv('GOOGLE_SHEET_ID')
                sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Sheet1')
                df = self.extractor.extract_from_google_sheets(sheet_id, sheet_name)
            else:
                csv_path = source_path or 'datasets/messy_students_raw.csv'
                df = self.extractor.extract_from_csv(csv_path)

            pipeline_report['extract'] = {
                'records_extracted': len(df),
                'columns': list(df.columns)
            }

            # TRANSFORM
            logger.info("\n[PHASE 2/3] TRANSFORM")
            logger.info("-" * 40)

            df_transformed, transform_report = self.transformer.transform(df)
            pipeline_report['transform'] = transform_report

            # LOAD
            logger.info("\n[PHASE 3/3] LOAD")
            logger.info("-" * 40)

            self.loader.connect()
            load_stats = self.loader.load(df_transformed)
            self.loader.disconnect()

            pipeline_report['load'] = load_stats

        except Exception as e:
            pipeline_report['status'] = 'FAILED'
            pipeline_report['error'] = str(e)
            logger.error(f"Pipeline failed: {e}")
            raise

        finally:
            end_time = datetime.now()
            pipeline_report['end_time'] = end_time.isoformat()
            pipeline_report['duration_seconds'] = (end_time - start_time).total_seconds()

            # Log final report
            self._log_report(pipeline_report)

        return pipeline_report

    def _log_report(self, report: Dict):
        """Log the final pipeline report"""
        logger.info("\n" + "=" * 60)
        logger.info("ETL PIPELINE REPORT")
        logger.info("=" * 60)

        logger.info(f"\nStatus: {report['status']}")
        logger.info(f"Duration: {report['duration_seconds']:.2f} seconds")

        logger.info(f"\nExtract Phase:")
        logger.info(f"  - Records extracted: {report['extract'].get('records_extracted', 0)}")

        logger.info(f"\nTransform Phase:")
        logger.info(f"  - Original count: {report['transform'].get('original_count', 0)}")
        logger.info(f"  - Final count: {report['transform'].get('final_count', 0)}")
        logger.info(f"  - Duplicates removed: {report['transform'].get('duplicates_removed', 0)}")
        logger.info(f"  - Validation errors: {len(report['transform'].get('validation_errors', []))}")

        logger.info(f"\nLoad Phase:")
        logger.info(f"  - Departments inserted: {report['load'].get('departments_inserted', 0)}")
        logger.info(f"  - Students inserted: {report['load'].get('students_inserted', 0)}")
        logger.info(f"  - Students updated: {report['load'].get('students_updated', 0)}")

        if report['transform'].get('validation_errors'):
            logger.info(f"\nValidation Errors:")
            for error in report['transform']['validation_errors'][:10]:
                logger.info(f"  - {error['field']}: {error['value']} - {error['error']}")

        logger.info("\n" + "=" * 60)
        logger.info(f"Log file: {log_file}")
        logger.info("=" * 60)

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='ETL Pipeline for Student Data')
    parser.add_argument(
        '--source',
        choices=['sheets', 'csv'],
        default='sheets',
        help='Data source: sheets (Google Sheets) or csv (local CSV)'
    )
    parser.add_argument(
        '--csv-path',
        default='datasets/messy_students_raw.csv',
        help='Path to CSV file (only used if source=csv)'
    )

    args = parser.parse_args()

    pipeline = ETLPipeline()

    try:
        report = pipeline.run(source=args.source, source_path=args.csv_path)

        if report['status'] == 'SUCCESS':
            print("\n" + "=" * 60)
            print("ETL PIPELINE COMPLETED SUCCESSFULLY")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("ETL PIPELINE FAILED")
            print("=" * 60)
            sys.exit(1)

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
