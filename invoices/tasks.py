from collections import defaultdict
from celery import shared_task
from .models import (
    Status, TimesheetInvoice, Project, Employee,
    TimeSheetFile, BillableRate, InvoiceSummary
)
from decimal import Decimal
import csv
from datetime import datetime
from django.db import transaction
from .utils import convert_decimal_to_string


@shared_task
def process_csv_file(file_id):
    """
    Task to process the uploaded CSV file and generate timesheets.
    """
    try:
        timesheet_file = TimeSheetFile.objects.get(id=file_id)
        if timesheet_file.status == Status.PROCESSED:
            return f"File {timesheet_file.id} has already been processed."
        
        csv_file = timesheet_file.file

        # Decode the CSV file
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        # List to hold the timesheet entries
        timesheet_entries = []
        batch_size = 100

        with transaction.atomic():
            # Process each row in the CSV file
            for row in reader:
                
                # Check if row is not empty or contains valid data
                if not any(row.values()):
                    continue  # Skip empty rows
                
                # Parse date and times
                date_str = row['Date']
                start_time_str = row['Start Time']
                end_time_str = row['End Time']

                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    start_time = datetime.strptime(start_time_str, '%H:%M').time()
                    end_time = datetime.strptime(end_time_str, '%H:%M').time()
                    
                    # Compute hours worked to be used in the creation of the TimesheetInvoice object
                    start_datetime = datetime.combine(date, start_time)
                    end_datetime = datetime.combine(date, end_time)
                                    
                except ValueError:
                    # If any row fails to parse, stop processing and roll back the transaction
                    raise ValueError(f"Failed to process file {file_id}. Date/Time format error in row {row}")

                # Get or create the project
                project_obj, _ = Project.objects.get_or_create(name=row['Project'])
                
                # Get or create the employee
                employee_obj, _ = Employee.objects.get_or_create(employee_id=row['Employee ID'])
                
                # Attempt to get the billable rate for the employee in the file
                billable_rate, created = BillableRate.objects.get_or_create(
                    file=timesheet_file,
                    employee=employee_obj,
                    defaults={'rate': Decimal(row['Billable Rate (per hour)'])}
                )
                
                if not created:
                    # Update the billable rate if it has changed
                    if billable_rate.rate != Decimal(row['Billable Rate (per hour)']):
                        raise ValueError(f"Billable rate for employee {employee_obj.employee_id} in same file can't have two different values.")

                # Add the TimesheetInvoice object to the list
                timesheet_entries.append(TimesheetInvoice(
                    file=timesheet_file,
                    employee=employee_obj,
                    project=project_obj,
                    billable_rate=billable_rate,
                    date=date,
                    start_time=start_time,
                    end_time=end_time
                ))
                
                # Bulk create when batch size is reached
                if len(timesheet_entries) >= batch_size:
                    TimesheetInvoice.objects.bulk_create(timesheet_entries)
                    timesheet_entries = []  # Reset the list

            # Process any remaining entries
            if timesheet_entries:
                TimesheetInvoice.objects.bulk_create(timesheet_entries)
        
        timesheet_file.status = Status.LOADED
        timesheet_file.save()

        # Trigger the summary computation task
        compute_invoice_summary.delay(file_id)

        return f"Read file {timesheet_file.id} successfully."

    except Exception as e:
        timesheet_file.status = Status.FAILED
        timesheet_file.error_message = f"Failed to read file {file_id}. Error: {str(e)}"
        timesheet_file.save()
        return f"Failed to read file {file_id}. Error: {str(e)}"


@shared_task
@transaction.atomic
def compute_invoice_summary(file_id):
    """
    Task to compute the summary of invoices grouped by projects for a specific file 
    and save the results.
    For each employee under a project, the total hours worked, unit price, and total cost are calculated.
    Finally, the total cost for each project is calculated.
    """
    
    try:
        
        timesheet_file = TimeSheetFile.objects.get(id=file_id)
        
        if timesheet_file.status != Status.LOADED:
            raise ValueError(f"File {file_id} has not been loaded yet.")    
        
        # Fetch all invoices related to the given file ID
        invoices = TimesheetInvoice.objects.filter(file_id=file_id).select_related('project', 'employee', 'billable_rate')
    
        # Dictionary to hold the grouped invoice data by project
        project_summary = defaultdict(list)

        # Track total cost for each project
        project_total_costs = {}

        # Group invoices by project and then by employee to calculate total hours and costs
        for project in invoices.values('project__name').distinct():

            project_name = project['project__name']

            # For each project, group and sum hours worked per employee
            employees_in_project = defaultdict(lambda: {'total_hours': Decimal('0.00'), 'unit_price': Decimal('0.00'), 'total_cost': Decimal('0.00')})

            for invoice in invoices.filter(project__name=project_name):

                employee_id = invoice.employee.employee_id
                unit_price = invoice.billable_rate.rate  # Unit price (billable rate) for this employee
                hours_worked = Decimal(invoice.hours_worked)  # Calculate hours worked

                # Update employee's total hours and cost
                employees_in_project[employee_id]['total_hours'] += hours_worked
                employees_in_project[employee_id]['unit_price'] = unit_price
                employees_in_project[employee_id]['total_cost'] += hours_worked * unit_price

            # Add the summarized data for each employee to the project summary
            project_total_cost = Decimal('0.00')
            
            for employee_id, employee_data in employees_in_project.items():
                project_summary[project_name].append({
                    'employee_id': employee_id,
                    'total_hours': employee_data['total_hours'],
                    'unit_price': employee_data['unit_price'],
                    'cost': employee_data['total_cost'],
                })
                # Add to the total cost for this project
                project_total_cost += employee_data['total_cost']

            # Store total cost for the project
            project_total_costs[project_name] = project_total_cost
            
        # Convert Decimal objects to string for JSON serialization
        project_summary_parsed = convert_decimal_to_string(project_summary)
        project_total_costs_parsed = convert_decimal_to_string(project_total_costs)
        
        # Save the summary to the database
        InvoiceSummary.objects.create(
            file_id=file_id,
            project_summary=project_summary_parsed,
            project_total_costs=project_total_costs_parsed
            )
        
        # Mark the file as fully processed if no errors occurred
        timesheet_file.status = Status.PROCESSED
        timesheet_file.save()

        return f"Invoice summary for file {file_id} has been computed and saved."
    
    except Exception as e:
        timesheet_file.status = Status.FAILED
        timesheet_file.error_message = f"Failed to compute invoice summary for file {file_id}. Error: {str(e)}"
        timesheet_file.save()
        return f"Failed to compute invoice summary for file {file_id}. Error: {str(e)}"
