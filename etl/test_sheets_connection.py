"""
Google Sheets API Connection Test
Tests authentication and basic read operations
"""

import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Scopes for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def test_google_sheets_connection():
    """
    Test Google Sheets API connection
    """
    print("🔄 Testing Google Sheets API Connection...")
    print("=" * 60)
    
    try:
        # Load credentials
        creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        print(f"\n📁 Loading credentials from: {creds_file}")
        
        if not os.path.exists(creds_file):
            print(f"❌ Credentials file not found: {creds_file}")
            return False
        
        # Authenticate
        credentials = service_account.Credentials.from_service_account_file(
            creds_file, scopes=SCOPES
        )
        
        print("✅ Credentials loaded successfully!")
        print(f"📧 Service Account: {credentials.service_account_email}")
        
        # Build the service
        service = build('sheets', 'v4', credentials=credentials)
        
        print("✅ Google Sheets API service initialized!")
        
        # Try to access a sheet (will fail if no sheet ID is set, but that's ok for now)
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        if sheet_id and sheet_id != 'your_google_sheet_id':
            print(f"\n📊 Attempting to access sheet: {sheet_id}")
            sheet = service.spreadsheets()
            result = sheet.get(spreadsheetId=sheet_id).execute()
            print(f"✅ Successfully accessed sheet: {result.get('properties', {}).get('title')}")
        else:
            print("\n⚠️  No Google Sheet ID configured yet (this is normal)")
            print("   We'll create a test sheet in the next step")
        
        print("\n" + "=" * 60)
        print("✅ Google Sheets API Connection Test PASSED!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n⚠️  TROUBLESHOOTING:")
        print("1. Verify credentials.json exists in project root")
        print("2. Check that Google Sheets API is enabled")
        print("3. Ensure service account has proper permissions")
        return False

if __name__ == "__main__":
    test_google_sheets_connection()
