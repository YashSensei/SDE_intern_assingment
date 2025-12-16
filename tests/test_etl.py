"""
ETL Pipeline Tests
Unit tests for data transformation and validation functions
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.etl import DataTransformer

class TestDataTransformer:
    """Tests for DataTransformer class"""

    @pytest.fixture
    def transformer(self):
        """Create a fresh transformer for each test"""
        return DataTransformer()

    # Email Validation Tests
    def test_clean_email_valid(self, transformer):
        """Test valid email cleaning"""
        assert transformer._clean_email("test@example.com") == "test@example.com"
        assert transformer._clean_email("  TEST@EXAMPLE.COM  ") == "test@example.com"

    def test_clean_email_invalid(self, transformer):
        """Test invalid email returns None"""
        assert transformer._clean_email("invalid-email") is None
        assert transformer._clean_email("") is None
        assert transformer._clean_email(None) is None
        assert transformer._clean_email("nan") is None

    # Department Mapping Tests
    def test_map_department_variations(self, transformer):
        """Test department name normalization"""
        assert transformer._map_department("CS") == "Computer Science"
        assert transformer._map_department("CompSci") == "Computer Science"
        assert transformer._map_department("Math") == "Mathematics"
        assert transformer._map_department("EE") == "Electrical Engineering"

    def test_map_department_already_normalized(self, transformer):
        """Test already normalized department names"""
        assert transformer._map_department("Computer Science") == "Computer Science"
        assert transformer._map_department("Mathematics") == "Mathematics"

    def test_map_department_unknown(self, transformer):
        """Test unknown department returns original"""
        assert transformer._map_department("Unknown Dept") == "Unknown Dept"

    def test_map_department_empty(self, transformer):
        """Test empty department returns None"""
        assert transformer._map_department("") is None
        assert transformer._map_department(None) is None

    # Status Mapping Tests
    def test_map_status_variations(self, transformer):
        """Test status normalization"""
        assert transformer._map_status("Active") == "active"
        assert transformer._map_status("ACTIVE") == "active"
        assert transformer._map_status("inactive") == "inactive"
        assert transformer._map_status("GRADUATED") == "graduated"

    def test_map_status_default(self, transformer):
        """Test default status"""
        assert transformer._map_status("") == "active"
        assert transformer._map_status(None) == "active"
        assert transformer._map_status("invalid") == "active"

    # Year Level Tests
    def test_clean_year_valid(self, transformer):
        """Test valid year levels"""
        assert transformer._clean_year("1") == 1
        assert transformer._clean_year("2") == 2
        assert transformer._clean_year(3) == 3
        assert transformer._clean_year("4.0") == 4

    def test_clean_year_out_of_range(self, transformer):
        """Test out of range years get clamped"""
        assert transformer._clean_year("5") == 4  # Clamped to max
        assert transformer._clean_year("0") == 1  # Clamped to min

    def test_clean_year_invalid(self, transformer):
        """Test invalid year returns None"""
        assert transformer._clean_year("") is None
        assert transformer._clean_year(None) is None
        assert transformer._clean_year("abc") is None

    # Phone Number Tests
    def test_clean_phone_10_digits(self, transformer):
        """Test 10-digit phone formatting"""
        assert transformer._clean_phone("5550101234") == "555-010-1234"
        assert transformer._clean_phone("(555) 010-1234") == "555-010-1234"
        assert transformer._clean_phone("555.010.1234") == "555-010-1234"

    def test_clean_phone_7_digits(self, transformer):
        """Test 7-digit phone formatting"""
        assert transformer._clean_phone("0101234") == "010-1234"

    def test_clean_phone_empty(self, transformer):
        """Test empty phone returns None"""
        assert transformer._clean_phone("") is None
        assert transformer._clean_phone(None) is None

    # Date Tests
    def test_clean_date_various_formats(self, transformer):
        """Test date parsing for various formats"""
        assert transformer._clean_date("2003-05-15") == "2003-05-15"
        assert transformer._clean_date("05/15/2003") == "2003-05-15"
        assert transformer._clean_date("05-15-2003") == "2003-05-15"

    def test_clean_date_invalid(self, transformer):
        """Test invalid date returns None"""
        assert transformer._clean_date("invalid") is None
        assert transformer._clean_date("") is None
        assert transformer._clean_date(None) is None

    # GPA Tests
    def test_clean_gpa_valid(self, transformer):
        """Test valid GPA cleaning"""
        assert transformer._clean_gpa("3.85") == 3.85
        assert transformer._clean_gpa(4.0) == 4.0
        assert transformer._clean_gpa("0") == 0.0

    def test_clean_gpa_out_of_range(self, transformer):
        """Test out of range GPA returns None"""
        assert transformer._clean_gpa("4.5") is None
        assert transformer._clean_gpa("-1") is None

    def test_clean_gpa_invalid(self, transformer):
        """Test invalid GPA returns None"""
        assert transformer._clean_gpa("##") is None
        assert transformer._clean_gpa("") is None
        assert transformer._clean_gpa(None) is None
        assert transformer._clean_gpa("abc") is None


class TestDataTransformIntegration:
    """Integration tests for full transformation"""

    @pytest.fixture
    def transformer(self):
        return DataTransformer()

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample messy data"""
        import pandas as pd

        data = {
            'Student ID': ['1', '2', '2', '3'],  # Note: duplicate ID
            'Email': ['test1@example.com', 'test2@example.com', 'test2@example.com', 'INVALID'],
            'First Name': ['John', 'Jane', 'Jane', 'Bob'],
            'Last Name': ['Doe', 'Smith', 'Smith', 'Williams'],
            'Year': ['1', '2', '2', '5'],
            'Department': ['CS', 'Math', 'Math', 'Physics'],
            'Status': ['Active', 'INACTIVE', 'INACTIVE', 'active'],
            'Phone': ['5550101', '(555) 010-2222', '(555) 010-2222', ''],
            'DOB': ['2003-05-15', '05/20/2004', '05/20/2004', '']
        }

        return pd.DataFrame(data)

    def test_removes_duplicates(self, transformer, sample_dataframe):
        """Test that duplicates are removed"""
        df, _ = transformer.transform(sample_dataframe)
        assert len(df) == 3  # Should remove 1 duplicate

    def test_normalizes_departments(self, transformer, sample_dataframe):
        """Test that departments are normalized"""
        df, _ = transformer.transform(sample_dataframe)
        assert 'Computer Science' in df['department'].values
        assert 'Mathematics' in df['department'].values

    def test_generates_report(self, transformer, sample_dataframe):
        """Test that transformation report is generated"""
        _, report = transformer.transform(sample_dataframe)
        assert 'original_count' in report
        assert 'final_count' in report
        assert 'duplicates_removed' in report
        assert report['duplicates_removed'] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
