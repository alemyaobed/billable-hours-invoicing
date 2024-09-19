import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Timesheet, Project, Employee
from django.shortcuts import render

def index(request):
    title = 'Index'
    return render(request, 'invoices/index.html', {'title': title})


def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES['csvFile']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV format.')
            return redirect('index')
        
        # Process CSV data
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                if not Project.objects.filter(name=row['Project']).exists():
                    new_project = Project.objects.create(name=row['Project'])
                if not Employee.objects.filter(employee_id=row['Employee ID']).exists():
                    new_employee = Employee.objects.create(employee_id=row['Employee ID'])
                    
                Timesheet.objects.create(
                    employee=new_employee,
                    billable_rate=row['Billable Rate (per hour)'],
                    project=new_project,
                    date=row['Date'],
                    start_time=row['Start Time'],
                    end_time=row['End Time']
                )
            messages.success(request, 'File uploaded successfully.')
        except Exception as e:
            messages.error(request, f'Error processing file: {e}')
        
        return redirect('home')
    
    return render(request, 'invoices/index.html')


