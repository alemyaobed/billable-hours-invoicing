"""
Unit tests for the models in the invoices app.
These tests cover the creation and validation of model instances.
"""
import uuid
from django.test import TestCase
from django.utils.timezone import now
from invoices.models import (
    TimeSheetFile, Employee, BillableRate, Project,
    TimesheetInvoice, InvoiceSummary,
)
from datetime import time, date
from decimal import Decimal


class TimeSheetFileModelTest(TestCase):
    """Test cases for the TimeSheetFile model."""

    def setUp(self):
        """Set up a TimeSheetFile instance for testing."""
        self.timesheet = TimeSheetFile.objects.create(
            file='timesheets/test.csv',
            status='PENDING',
        )

    def test_timesheet_file_creation(self):
        """Test that the TimeSheetFile is created with correct attributes."""
        self.assertTrue(TimeSheetFile.objects.filter(file='timesheets/test.csv').exists())
        self.assertIsNotNone(self.timesheet.id)
        self.assertIsInstance(self.timesheet.id, uuid.UUID)
        self.assertEqual(self.timesheet.id.version, 4)
        self.assertEqual(self.timesheet.file, 'timesheets/test.csv')
        self.assertEqual(self.timesheet.status, 'PENDING')
        self.assertIsNone(self.timesheet.error_message)
        self.assertIsNotNone(self.timesheet.uploaded_at)


class EmployeeModelTest(TestCase):
    """Test cases for the Employee model."""

    def setUp(self):
        """Set up an Employee instance for testing."""
        self.employee = Employee.objects.create(employee_id=1234)

    def test_employee_creation(self):
        """Test that the Employee is created with correct attributes."""
        self.assertEqual(self.employee.employee_id, 1234)
        self.assertTrue(Employee.objects.filter(employee_id=1234).exists())


class BillableRateModelTest(TestCase):
    """Test cases for the BillableRate model."""

    def setUp(self):
        """Set up instances for testing BillableRate."""
        self.timesheet = TimeSheetFile.objects.create(
            file='timesheets/test.csv',
            status='PENDING',
        )
        self.employee = Employee.objects.create(employee_id=1234)
        self.billable_rate = BillableRate.objects.create(
            file=self.timesheet,
            employee=self.employee,
            rate=Decimal('100.00')
        )

    def test_billable_rate_creation(self):
        """Test that the BillableRate is created with correct attributes."""
        self.assertEqual(self.billable_rate.file, self.timesheet)
        self.assertEqual(self.billable_rate.employee, self.employee)
        self.assertEqual(self.billable_rate.rate, Decimal('100.00'))

class TimesheetInvoiceModelTest(TestCase):
    """Test cases for the TimesheetInvoice model."""

    def setUp(self):
        """Set up instances for testing TimesheetInvoice."""
        self.timesheet = TimeSheetFile.objects.create(
            file='timesheets/test.csv',
            status='PENDING',
        )
        self.employee = Employee.objects.create(employee_id=1234)
        self.project = Project.objects.create(name="Test Project")
        self.billable_rate = BillableRate.objects.create(
            file=self.timesheet,
            employee=self.employee,
            rate=Decimal('100.00')
        )
        self.invoice = TimesheetInvoice.objects.create(
            file=self.timesheet,
            employee=self.employee,
            project=self.project,
            billable_rate=self.billable_rate,
            date=date(2023, 1, 1),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_timesheet_invoice_creation(self):
        """Test that the TimesheetInvoice is created with correct attributes."""
        self.assertEqual(self.invoice.file, self.timesheet)
        self.assertEqual(self.invoice.employee, self.employee)
        self.assertEqual(self.invoice.project, self.project)
        self.assertEqual(self.invoice.billable_rate, self.billable_rate)
        self.assertEqual(self.invoice.hours_worked, 8)

class InvoiceSummaryModelTest(TestCase):
    """Test cases for the InvoiceSummary model."""

    def setUp(self):
        """Set up instances for testing InvoiceSummary."""
        self.timesheet = TimeSheetFile.objects.create(
            file='timesheets/test.csv',
            status='PENDING',
        )
        self.summary = InvoiceSummary.objects.create(
            file=self.timesheet,
            project_summary={"Test Project": "Summary"},
            project_total_costs={"Test Project": 1000}
        )

    def test_invoice_summary_creation(self):
        """Test that the InvoiceSummary is created with correct attributes."""
        self.assertEqual(self.summary.file, self.timesheet)
        self.assertEqual(self.summary.project_summary, {"Test Project": "Summary"})
        self.assertEqual(self.summary.project_total_costs, {"Test Project": 1000})
