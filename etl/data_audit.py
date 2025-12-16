"""
Data Audit Script - Analyze messy Google Sheets data
Identifies duplicates, missing values, inconsistencies, and data quality issues
"""

import os
import pandas as pd
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from collections import Counter
import re

# Load environment variables
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheets_service():
    """Initialize Google Sheets API service"""
    creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    credentials = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=credentials)

def read_sheet_data():
    """Read data from Google Sheet"""
    service = get_sheets_service()
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    range_name = os.getenv('GOOGLE_SHEET_NAME', 'Table1')
    
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()
    
    values = result.get('values', [])
    
    if not values:
        return None
    
    # Convert to DataFrame
    headers = values[0]
    data = values[1:]
    df = pd.DataFrame(data, columns=headers)
    
    return df

def analyze_data_quality(df):
    """Perform comprehensive data quality analysis"""
    
    print("=" * 80)
    print("📊 DATA AUDIT REPORT - MESSY STUDENT DATA")
    print("=" * 80)
    
    print(f"\n📌 DATASET OVERVIEW")
    print(f"   Total Records: {len(df)}")
    print(f"   Total Columns: {len(df.columns)}")
    print(f"   Columns: {', '.join(df.columns)}")
    
    # 1. DUPLICATE ANALYSIS
    print(f"\n" + "=" * 80)
    print("❌ ISSUE #1: DUPLICATE RECORDS")
    print("=" * 80)
    
    # Check for duplicate Student IDs
    if 'Student ID' in df.columns:
        duplicate_ids = df[df.duplicated(subset=['Student ID'], keep=False)]
        if not duplicate_ids.empty:
            print(f"   Found {len(duplicate_ids)} duplicate Student ID records:")
            for idx, row in duplicate_ids.iterrows():
                print(f"   - Row {idx+2}: Student ID {row.get('Student ID', 'N/A')} - {row.get('First Name', '')} {row.get('Last Name', '')}")
        else:
            print("   ✅ No duplicate Student IDs found")
    
    # Check for duplicate emails
    if 'Email' in df.columns:
        email_col = df['Email'].fillna('')
        duplicate_emails = df[email_col.duplicated(keep=False) & (email_col != '')]
        if not duplicate_emails.empty:
            print(f"\n   Found {len(duplicate_emails)} duplicate Email records:")
            for idx, row in duplicate_emails.iterrows():
                print(f"   - Row {idx+2}: {row.get('Email', 'N/A')}")
    
    # 2. MISSING VALUES
    print(f"\n" + "=" * 80)
    print("❌ ISSUE #2: MISSING VALUES")
    print("=" * 80)
    
    for col in df.columns:
        missing_count = df[col].isna().sum() + (df[col] == '').sum()
        if missing_count > 0:
            missing_pct = (missing_count / len(df)) * 100
            print(f"   {col:<20}: {missing_count:>3} missing ({missing_pct:>5.1f}%)")
            # Show which rows
            missing_rows = df[df[col].isna() | (df[col] == '')].index.tolist()
            print(f"      Rows: {[r+2 for r in missing_rows]}")
    
    # 3. INCONSISTENT FORMATTING
    print(f"\n" + "=" * 80)
    print("❌ ISSUE #3: INCONSISTENT FORMATTING")
    print("=" * 80)
    
    # Department variations
    if 'Department' in df.columns:
        dept_values = df['Department'].value_counts()
        print(f"\n   Department Name Variations:")
        for dept, count in dept_values.items():
            print(f"   - '{dept}': {count} records")
        
        # Identify similar departments
        dept_groups = {
            'Computer Science': ['CS', 'CompSci', 'Computer Science'],
            'Mathematics': ['Math', 'Mathematics', 'MATH'],
            'Business Administration': ['Business', 'Business Administration'],
            'Electrical Engineering': ['EE', 'Electrical Engineering']
        }
        print(f"\n   Suggested Mapping:")
        for standard, variations in dept_groups.items():
            found_vars = [v for v in variations if v in dept_values.index]
            if found_vars:
                print(f"   - {standard}: {found_vars}")
    
    # Status case variations
    if 'Status' in df.columns:
        status_values = df['Status'].value_counts()
        print(f"\n   Status Case Variations:")
        for status, count in status_values.items():
            print(f"   - '{status}': {count} records")
    
    # Phone number formats
    if 'Phone' in df.columns:
        phone_values = df['Phone'].dropna()
        phone_formats = phone_values[phone_values != ''].tolist()
        if phone_formats:
            print(f"\n   Phone Number Format Variations:")
            unique_formats = set(phone_formats)
            for fmt in list(unique_formats)[:5]:  # Show first 5
                print(f"   - '{fmt}'")
    
    # Date formats
    if 'DOB' in df.columns:
        dob_values = df['DOB'].dropna()
        dob_formats = dob_values[dob_values != ''].tolist()
        if dob_formats:
            print(f"\n   Date Format Variations:")
            for fmt in list(set(dob_formats))[:5]:
                print(f"   - '{fmt}'")
    
    # 4. DATA VALIDATION ISSUES
    print(f"\n" + "=" * 80)
    print("❌ ISSUE #4: DATA VALIDATION ERRORS")
    print("=" * 80)
    
    # Invalid emails
    if 'Email' in df.columns:
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        invalid_emails = df[~df['Email'].str.match(email_pattern, na=False) & (df['Email'] != '')]
        if not invalid_emails.empty:
            print(f"\n   Invalid Email Formats ({len(invalid_emails)} records):")
            for idx, row in invalid_emails.iterrows():
                print(f"   - Row {idx+2}: '{row.get('Email', 'N/A')}'")
    
    # Invalid year levels
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        invalid_years = df[(df['Year'] < 1) | (df['Year'] > 4)]
        if not invalid_years.empty:
            print(f"\n   Invalid Year Levels ({len(invalid_years)} records):")
            for idx, row in invalid_years.iterrows():
                print(f"   - Row {idx+2}: Year {row.get('Year', 'N/A')} (should be 1-4)")
    
    # Missing GPA
    if 'GPA' in df.columns:
        missing_gpa = df[df['GPA'].isna() | (df['GPA'] == '') | (df['GPA'] == '##')]
        if not missing_gpa.empty:
            print(f"\n   Missing/Invalid GPA ({len(missing_gpa)} records):")
            for idx, row in missing_gpa.iterrows():
                print(f"   - Row {idx+2}: Student ID {row.get('Student ID', 'N/A')}")
    
    # 5. SUMMARY
    print(f"\n" + "=" * 80)
    print("📋 SUMMARY OF DATA QUALITY ISSUES")
    print("=" * 80)
    
    total_issues = 0
    
    # Count issues
    duplicate_count = len(df[df.duplicated(subset=['Student ID'], keep=False)])
    missing_critical = (df['Email'].isna() | (df['Email'] == '')).sum()
    
    print(f"\n   1. Duplicate Records: {duplicate_count}")
    print(f"   2. Missing Critical Fields: {missing_critical}")
    print(f"   3. Inconsistent Department Names: {len(dept_values) if 'Department' in df.columns else 0} variations")
    print(f"   4. Inconsistent Status Values: {len(status_values) if 'Status' in df.columns else 0} variations")
    print(f"   5. Invalid Email Formats: {len(invalid_emails) if 'Email' in df.columns else 0}")
    
    print(f"\n   📊 Data Quality Score: {max(0, 100 - (duplicate_count + missing_critical) * 5)}%")
    
    print(f"\n" + "=" * 80)
    print("✅ AUDIT COMPLETE")
    print("=" * 80)
    
    return df

def main():
    """Main execution"""
    try:
        print("\n🔄 Reading data from Google Sheets...")
        df = read_sheet_data()
        
        if df is None:
            print("❌ No data found in sheet")
            return
        
        print(f"✅ Successfully loaded {len(df)} records\n")
        
        # Perform audit
        analyze_data_quality(df)
        
        # Save raw data to CSV for reference
        output_file = 'datasets/messy_students_raw.csv'
        df.to_csv(output_file, index=False)
        print(f"\n💾 Raw data saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
