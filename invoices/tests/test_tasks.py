"""
Unit tests for processing timesheet files and computing invoice summaries in the invoices application.

This test suite verifies the functionality of the timesheet processing system, including the successful 
processing of CSV files, handling of errors such as invalid formats or conflicting data, and the correct 
computation of invoice summaries.

Test Cases:
- test_process_csv_file_success: Tests successful processing of a valid CSV file and checks for the 
  correct creation of TimesheetInvoice objects.
  
- test_process_csv_file_already_processed: Verifies that an appropriate message is returned when trying 
  to process an already processed file.

- test_file_not_loaded: Tests that an error message is returned when attempting to compute the invoice 
  summary for a file that has not been loaded.

- test_process_csv_file_invalid_date_format: Ensures that the system correctly fails when provided with 
  an invalid date format in the CSV file.

- test_process_csv_file_billable_rate_conflict: Tests the behavior of the system when the CSV file 
  contains conflicting billable rates for the same employee.

- test_compute_invoice_summary_correct_values: Verifies that the computed invoice summary reflects the 
  correct total costs and project summaries based on the processed timesheet data.

Setup:
- The `setUp` method creates a mock timesheet file in a pending state to be used in the tests. 
"""

from time import sleep
from django.test import TestCase
from unittest import mock
from invoices.models import (
    Employee, Project, TimeSheetFile, BillableRate, TimesheetInvoice, Status, InvoiceSummary
)
from invoices.utils import convert_decimal_to_string
from decimal import Decimal
from django.core.files.base import ContentFile
from invoices.tasks import process_csv_file, compute_invoice_summary


class TimeSheetProcessingTests(TestCase):
    
    def setUp(self):        
        # Create a timesheet file to be processed
        self.timesheet_file = TimeSheetFile.objects.create(
            file=ContentFile("Employee ID,Billable Rate (per hour),Project,Date,Start Time,End Time\n"
                             "1,300,Google,2019-07-01,09:00,17:00\n"
                             "2,100,Facebook,2019-07-01,11:00,16:00", name='test.csv'),
            status=Status.PENDING
        )
    
    @mock.patch('invoices.tasks.compute_invoice_summary.delay')
    def test_process_csv_file_success(self, mock_compute_invoice_summary):
        # Call the task to process the CSV file
        result = process_csv_file(self.timesheet_file.id)
        
        # Check if the file status was updated correctly
        self.timesheet_file.refresh_from_db()
        self.assertEqual(self.timesheet_file.status, Status.LOADED)
        self.assertEqual(result, f"Read file {self.timesheet_file.id} successfully.")
        
        # Ensure TimesheetInvoice objects are created
        self.assertEqual(TimesheetInvoice.objects.count(), 2)
        
        # Ensure that compute_invoice_summary is triggered
        mock_compute_invoice_summary.assert_called_once_with(self.timesheet_file.id)

    def test_process_csv_file_already_processed(self):
        # Set the status to PROCESSED
        self.timesheet_file.status = Status.PROCESSED
        self.timesheet_file.save()

        # Call the task to process the CSV file
        result = process_csv_file(self.timesheet_file.id)
        
        # Check that it returns an appropriate message
        self.assertEqual(result, f"File {self.timesheet_file.id} has already been processed.")
    
    def test_file_not_loaded(self):
        # Set the status to FAILED
        self.timesheet_file.status = Status.FAILED
        self.timesheet_file.save()

        # Try to compute the invoice summary
        result = compute_invoice_summary(self.timesheet_file.id)
        
        # Check that it returns an appropriate message
        self.assertEqual(result, f"Failed to compute invoice summary for file {self.timesheet_file.id}. Error: File {self.timesheet_file.id} has not been loaded yet.")
        
    def test_process_csv_file_invalid_date_format(self):
        # Create a CSV file with an invalid date format
        self.timesheet_file.file = ContentFile("Employee ID,Billable Rate (per hour),Project,Date,Start Time,End Time\n"
                                               "1,300,Google,07-01-2019,09:00,17:00", name='test_invalid.csv')
        self.timesheet_file.save()

        # Call the task to process the CSV file and expect a failure
        result = process_csv_file(self.timesheet_file.id)

        # Check the file status and error message
        self.timesheet_file.refresh_from_db()
        self.assertEqual(self.timesheet_file.status, Status.FAILED)
        self.assertIn("Date/Time format error", result)

    def test_process_csv_file_billable_rate_conflict(self):
        # Create a CSV file with conflicting billable rates
        self.timesheet_file.file = ContentFile("Employee ID,Billable Rate (per hour),Project,Date,Start Time,End Time\n"
                                               "1,300,Google,2019-07-01,09:00,17:00\n"
                                               "1,350,Google,2019-07-02,09:00,17:00", name='test_conflict.csv')
        self.timesheet_file.save()

        # Call the task to process the CSV file and expect a failure
        result = process_csv_file(self.timesheet_file.id)

        # Check the file status and error message
        self.timesheet_file.refresh_from_db()
        self.assertEqual(self.timesheet_file.status, Status.FAILED)
        self.assertIn("Billable rate for employee 1 in same file can't have two different values", result)

    
    def test_compute_invoice_summary_correct_values(self):
        # Create a new timesheet file to be processed
        self.new_timesheet = TimeSheetFile.objects.create(
            file=ContentFile("Employee ID,Billable Rate (per hour),Project,Date,Start Time,End Time\n"
                                               "1,300,Google,2019-07-01,09:00,17:00\n"
                                               "2,150,Google,2019-07-01,10:00,15:00\n"
                                                "3,200,Apple,2019-07-01,11:45,16:00\n"
                                               "4,350,Apple,2019-07-02,09:30,17:00", name='test_file.csv'),
            status=Status.PENDING
        )
        
        self.assertEqual(self.new_timesheet.status, Status.PENDING)
        file = self.new_timesheet
        
        # Create projects, employees, billable rates, and timesheet invoices
        project_google = Project.objects.create(name='Google')
        project_apple = Project.objects.create(name='Apple')

        employee1 = Employee.objects.create(employee_id=1)
        employee2 = Employee.objects.create(employee_id=2)
        employee3 = Employee.objects.create(employee_id=3)
        employee4 = Employee.objects.create(employee_id=4)

        billable_rate1 = BillableRate.objects.create(file=file, employee=employee1, rate=300)
        billable_rate2 = BillableRate.objects.create(file=file, employee=employee2, rate=150)
        billable_rate3 = BillableRate.objects.create(file=file, employee=employee3, rate=200)
        billable_rate4 = BillableRate.objects.create(file=file, employee=employee4, rate=350)

        TimesheetInvoice.objects.create(
            file=file,
            employee=employee1,
            project=project_google,
            billable_rate=billable_rate1,
            date='2019-07-01',
            start_time='09:00',
            end_time='17:00'  # 8 hours
        )
        TimesheetInvoice.objects.create(
            file=file,
            employee=employee2,
            project=project_google,
            billable_rate=billable_rate2,
            date='2019-07-01',
            start_time='10:00',
            end_time='15:00'  # 5 hours
        )
        TimesheetInvoice.objects.create(
            file=file,
            employee=employee3,
            project=project_apple,
            billable_rate=billable_rate3,
            date='2019-07-01',
            start_time='11:45',
            end_time='16:00'  # 5 hours
        )
        TimesheetInvoice.objects.create(
            file=file,
            employee=employee4,
            project=project_apple,
            billable_rate=billable_rate4,
            date='2019-07-01',
            start_time='09:30',
            end_time='17:00'
        )
        
        file.status = Status.LOADED
        file.save()

        # Run the task
        compute_invoice_summary(file.id)
        
        # Wait for the task to complete
        sleep(10)
        
        # Change the status to PROCESSED
        file.refresh_from_db() 
        
        self.assertEqual(file.status, Status.PROCESSED)

        # Fetch the created InvoiceSummary
        summary = InvoiceSummary.objects.get(file=file)

        # Validate the project summary
        project_summary = summary.project_summary
        project_total_costs = summary.project_total_costs

        # Parse the summaries to check the values
        expected_summary = {
            'Google': [
                {
                    'employee_id': employee1.employee_id,
                    'total_hours': Decimal('8.00'),  # Employee 1 worked 8 hours
                    'unit_price': Decimal('300'),
                    'cost': Decimal('2400.00')  # 8 hours * 300
                },
                {
                    'employee_id': employee2.employee_id,
                    'total_hours': Decimal('5.00'),  # Employee 2 worked 5 hours
                    'unit_price': Decimal('150'),
                    'cost': Decimal('750.00')  # 5 hours * 150
                }
            ],
            'Apple': [
                {
                    'employee_id': employee3.employee_id,
                    'total_hours': Decimal('4.25'),  # Employee 3 worked 4.25 hours
                    'unit_price': Decimal('200'),
                    'cost': Decimal('850.00')  # 4.25 hours * 200
                },
                {
                    'employee_id': employee4.employee_id,
                    'total_hours': Decimal('7.50'),  # Employee 4 worked 7.5 hours
                    'unit_price': Decimal('350'),
                    'cost': Decimal('2625.00')  # 7.5 hours * 350
                }
            ]
        }

        expected_total_costs = {
            'Google': Decimal('3150.00'),  # 2400 + 750
            'Apple': Decimal('3475.00')    # 850 + 2625
        }
        
        # Convert to string
        expected_summary = convert_decimal_to_string(expected_summary)
        expected_total_costs = convert_decimal_to_string(expected_total_costs)

        # Check that the project summary matches the expected summary
        self.assertEqual(project_summary, expected_summary)

        # Check that the total costs match the expected total costs
        self.assertEqual(project_total_costs, expected_total_costs)
