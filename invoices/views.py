import csv
from django.shortcuts import render
from django.http import HttpResponse
from .models import Timesheet, Invoice

def upload_timesheet(request):
    if request.method == 'POST':
        csv_file = request.FILES['file']  # Assuming the file is uploaded via a form
        if not csv_file.name.endswith('.csv'):
            return HttpResponse('Please upload a CSV file.')

        # Parse the CSV file and save the timesheet entries
        reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
        for row in reader:
            employee_id, billable_rate, project, date, start_time, end_time = row
            Timesheet.objects.create(
                employee_id=employee_id,
                billable_rate=billable_rate,
                project_name=project,
                company_name=project,  # Assuming the project name is the company name
                date=date,
                start_time=start_time,
                end_time=end_time
            )

        return HttpResponse('Timesheet uploaded successfully.')

    return render(request, 'upload_timesheet.html')  # Add a form in the template to upload CSV

def generate_invoices(request):
    companies = Timesheet.objects.values_list('company_name', flat=True).distinct()
    for company in companies:
        Invoice.generate_invoice(company)

    return HttpResponse('Invoices generated successfully.')

