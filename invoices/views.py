from collections import defaultdict
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import  InvoiceSummary, TimeSheetFile, TimesheetInvoice
from .tasks import process_csv_file
from django.template.loader import render_to_string

def index(request):
    """
    Render the index page where the user can upload a CSV file.
    """
    title = 'Billable Hours'
    return render(request, 'invoices/index.html', {'title': title})


def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csvFile')
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'error': 'File is not CSV format.'}, status=400)
        # Save the uploaded CSV file to the TimeSheetFile model
        timesheet_file = TimeSheetFile.objects.create(file=csv_file)

        # Trigger Celery task to process the CSV file asynchronously
        process_csv_file.delay(timesheet_file.id)

        # Return a JSON response with the file ID for status checking
        return JsonResponse({'message': 'File uploaded successfully', 'file_id': timesheet_file.id})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def upload_status(request, file_id):
    """
    Returns the processing status of the uploaded CSV file.
    """
    try:
        timesheet_file = TimeSheetFile.objects.get(id=file_id)
        return JsonResponse({'status': 'processed' if timesheet_file.is_fully_processed else 'processing'})
    except TimeSheetFile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'File not found.'})


def view_invoices(request, file_id):
    """
    View to display the invoice summary for a specific file.
    """
    # Get the InvoiceSummary for the given file_id
    invoice_summary = get_object_or_404(InvoiceSummary, file__id=file_id)

    # Pass the invoice summary data to the template
    context = {
        'file_id': file_id,
        'project_summary': invoice_summary.project_summary.items(),
        'project_total_costs': invoice_summary.project_total_costs,
    }

    return render(request, 'invoices/invoices_summary.html', context)

