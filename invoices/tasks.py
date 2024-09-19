# invoices/tasks.py
from celery import shared_task
from .models import Timesheet, Project, Employee, TimeSheetFile, Invoice
from decimal import Decimal
import csv

@shared_task
def process_csv_file(file_id):
    """
    Task to process the uploaded CSV file and generate timesheets and invoices.
    """
    try:
        timesheet_file = TimeSheetFile.objects.get(id=file_id)
        csv_file = timesheet_file.file

        # Decode the CSV file
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        for row in reader:
            # Get or create the project
            project_obj, _ = Project.objects.get_or_create(name=row['Project'])
            
            # Get or create the employee
            employee_obj, _ = Employee.objects.get_or_create(employee_id=row['Employee ID'])
            
            # Create Timesheet entry
            timesheet = Timesheet.objects.create(
                file=timesheet_file,
                employee=employee_obj,
                project=project_obj,
                billable_rate=Decimal(row['Billable Rate (per hour)']),
                date=row['Date'],
                start_time=row['Start Time'],
                end_time=row['End Time']
            )

            # Create Invoice for each timesheet
            Invoice.objects.create(
                file=timesheet_file,
                employee=employee_obj,
                number_of_hours=timesheet.hours_worked,
                unit_price=timesheet.billable_rate,
                cost=timesheet.hours_worked * timesheet.billable_rate,  # Total cost calculation
            )
        
        return f"Processed file {timesheet_file.id} successfully."

    except Exception as e:
        return f"Failed to process file {file_id}. Error: {str(e)}"
