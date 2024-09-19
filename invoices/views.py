from collections import defaultdict
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import  TimeSheetFile, Invoice
from .tasks import process_csv_file

def index(request):
    """
    Render the index page where the user can upload a CSV file.
    """
    title = 'Billable Hours'
    return render(request, 'invoices/index.html', {'title': title})


def upload_csv(request):
    """
    Handle CSV file upload, process the timesheet data, and generate invoices.
    """
    if request.method == 'POST':
        csv_file = request.FILES['csvFile']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV format.')
            return redirect('index')
        
        # Save the uploaded CSV file to the TimeSheetFile model
        timesheet_file = TimeSheetFile.objects.create(file=csv_file)
        
        # Trigger Celery task to process the CSV file asynchronously
        process_csv_file.delay(timesheet_file.id)
        
                
        messages.success(request, 'File uploaded successfully. It is being processed.')
        return redirect('index')

    return render(request, 'invoices/index.html')


def view_invoices(request):
    """
    Display a list of all invoices grouped by file and then by project.
    """
    invoices = Invoice.objects.select_related('file', 'project', 'employee').all()

    # Group invoices by file, then by project
    grouped_invoices = defaultdict(lambda: defaultdict(list))

    for invoice in invoices:
        grouped_invoices[invoice.file][invoice.employee.project.name].append(invoice)

    return render(request, 'invoices/invoices.html', {'grouped_invoices': grouped_invoices})


