"""
This module contains integration tests for the views in the invoices app.
These tests verify the functionality of the upload_csv view, ensuring it 
correctly handles different scenarios for uploading CSV files, including 
valid and invalid inputs.
"""
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

class TimeSheetCSVUploadTest(TestCase):
    def setUp(self):
        """Set up test client and URL."""
        self.client = Client()
        self.upload_url = reverse('upload_csv')
    
    def test_no_file_uploaded(self):
        """Test upload_csv view if no file uploaded."""
        response = self.client.post(self.upload_url)
        expected_error = 'No file was uploaded.'
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': expected_error})
    
    def test_file_extension(self):
        """Test upload_csv view with a file not in CSV format."""
        invalid_file = SimpleUploadedFile("invalid.txt", b"file_content", content_type="text/plain")
        response = self.client.post(self.upload_url, {'csvFile': invalid_file})
        expected_error = 'File is not in CSV format. Please upload a CSV file.'
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': expected_error})

    def test_valid_csv_upload(self):
        """Test uploading a valid CSV file."""
        valid_csv = b"""Employee ID,Billable Rate (per hour),Project,Date,Start Time,End Time
                        101,50,Website Development,2024-09-01,09:00,17:00
                        102,60,Mobile App,2024-09-01,10:00,15:00
                        103,45,API Development,2024-09-02,08:00,12:00"""
        uploaded_file = SimpleUploadedFile("valid.csv", valid_csv, content_type="text/csv")
        
        response = self.client.post(self.upload_url, {'csvFile': uploaded_file})

        self.assertEqual(response.status_code, 200)
        # Check that the response contains the expected message and file_id
        expected_response = {
            'message': 'File uploaded successfully. Processing commenced.',
            'file_id': response.json().get('file_id')  # You may want to assert the specific file_id if needed
        }
        
        self.assertJSONEqual(response.content, expected_response)

    def test_invalid_header_format(self):
        """Test uploading a CSV file with invalid header format."""
        invalid_csv = b"""Emp ID,Billable Rate,Project Name,Date,Start,End
                        101,50,Website Development,2024-09-01,09:00,17:00"""
        uploaded_file = SimpleUploadedFile("invalid_header.csv", invalid_csv, content_type="text/csv")
        
        response = self.client.post(self.upload_url, {'csvFile': uploaded_file})
        expected_error = 'Invalid CSV file. Please ensure the file has the correct headers in their right/specified order.'
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': expected_error})
    
    def test_first_row_empty(self):
        """Test uploading a CSV file with the first row empty and not being the header."""
        empty_first_row_csv = b"""\n
                        101,50,Website Development,2024-09-01,09:00,17:00"""
        uploaded_file = SimpleUploadedFile("empty_first_row.csv", empty_first_row_csv, content_type="text/csv")
        
        response = self.client.post(self.upload_url, {'csvFile': uploaded_file})
        expected_error = 'CSV file does not contain a header or does not conform to the guidelines! Please read the guidelines.'
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': expected_error})
    
    def test_only_header_no_rows(self):
        """Test uploading a CSV file with only the header and no subsequent data rows."""
        header_only_csv = b"""Employee ID,Billable Rate (per hour),Project,Date,Start Time,End Time"""
        uploaded_file = SimpleUploadedFile("header_only.csv", header_only_csv, content_type="text/csv")
        
        response = self.client.post(self.upload_url, {'csvFile': uploaded_file})
        expected_error = 'CSV file contains only the header.'
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': expected_error})
    
    

    def test_missing_columns(self):
        """Test uploading a CSV file with missing columns."""
        missing_column_csv = b"""Employee ID,Project,Date,Start Time,End Time
                        101,Website Development,2024-09-01,09:00,17:00"""
        uploaded_file = SimpleUploadedFile("missing_columns.csv", missing_column_csv, content_type="text/csv")
        
        response = self.client.post(self.upload_url, {'csvFile': uploaded_file})
        expected_error = 'Invalid CSV file. Please ensure the file has the correct headers in their right/specified order.'
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': expected_error})

    def test_empty_file(self):
        """Test uploading an empty CSV file."""
        empty_csv = b""
        uploaded_file = SimpleUploadedFile("empty.csv", empty_csv, content_type="text/csv")
        
        response = self.client.post(self.upload_url, {'csvFile': uploaded_file})
        expected_error = 'File is empty.'
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': expected_error})
        
    ################################################################################################################
    ###
    ### Didn't implement these tests in the snippet because it would require polling for the file processing status
    ###
    ################################################################################################################
    # def test_duplicate_billable_rate(self):
    #     """Test uploading a CSV file with duplicate employee billable rates."""
    #     duplicate_rate_csv = b"""Employee ID,Billable Rate (per hour),Project,Date,Start Time,End Time
    #                     101,50,Website Development,2024-09-01,09:00,17:00
    #                     101,60,Website Development,2024-09-01,09:00,17:00"""
    #     uploaded_file = SimpleUploadedFile("duplicate_rate.csv", duplicate_rate_csv, content_type="text/csv")
        
    #     response = self.client.post(self.upload_url, {'csvFile': uploaded_file})
    #     self.assertEqual(response.status_code, 400)
    #     self.assertContains(response, "Duplicate entries with different billable rates for the same employee")

    # def test_invalid_date_format(self):
    #     """Test uploading a CSV file with invalid date format."""
    #     invalid_date_csv = b"""Employee ID,Billable Rate (per hour),Project,Date,Start Time,End Time
    #                     101,50,Website Development,01/09/2024,09:00,17:00"""
    #     uploaded_file = SimpleUploadedFile("invalid_date.csv", invalid_date_csv, content_type="text/csv")
        
    #     response = self.client.post(self.upload_url, {'csvFile': uploaded_file})
    #     self.assertEqual(response.status_code, 400)
    #     self.assertContains(response, "Invalid date format")

    def test_empty_rows(self):
        """Test uploading a CSV file with some empty rows."""
        empty_rows_csv = b"""Employee ID,Billable Rate (per hour),Project,Date,Start Time,End Time

                        101,50,Website Development,2024-09-01,09:00,17:00

                        102,60,Mobile App,2024-09-01,10:00,15:00"""
        uploaded_file = SimpleUploadedFile("empty_rows.csv", empty_rows_csv, content_type="text/csv")
        
        response = self.client.post(self.upload_url, {'csvFile': uploaded_file})
        # Check that the response contains the expected message and file_id
        expected_response = {
            'message': 'File uploaded successfully. Processing commenced.',
            'file_id': response.json().get('file_id')  # You may want to assert the specific file_id if needed
        }
        
        self.assertJSONEqual(response.content, expected_response)