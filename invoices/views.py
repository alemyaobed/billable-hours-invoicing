import csv
from io import TextIOWrapper
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import  InvoiceSummary, Status, TimeSheetFile
from .tasks import process_csv_file


def index(request):
    """
    Render the index page where the user can upload a CSV file.
    """
    title = 'Billable Hours'
    return render(request, 'invoices/index.html', {'title': title})


def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csvFile')
        
        if not csv_file:
            return JsonResponse({'error': 'No file was uploaded.'}, status=400)
        
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'error': 'File is not in CSV format.'}, status=400)
        
        if csv_file.size == 0:
            return JsonResponse({'error': 'File is empty.'}, status=400)
        
        # Expected headers in the exact order
        expected_headers = [
            'Employee ID',
            'Billable Rate (per hour)',
            'Project',
            'Date',
            'Start Time',
            'End Time'
        ]            
        
        # Open and read the CSV file to check if it's empty
        try:
            # Read the CSV content
            decoded_file = TextIOWrapper(csv_file, encoding='utf-8')
            csv_reader = csv.reader(decoded_file)

            # Skip the header row (assuming the first row is the header)
            header = next(csv_reader, None)
            
            if not header:
                return JsonResponse(
                    {'error': 'CSV file is empty or does not conform to the guidelines! Please read the guidelines.'}, status=400)

            # Check if the header row matches the expected headers
            if header != expected_headers:
                return JsonResponse(
                    {'error': 'Invalid CSV file. Please ensure the file has the correct headers in their right/specified order.'}, status=400)

            # Check if there are any rows after the header
            if not any(csv_reader):
                return JsonResponse({'error': 'CSV file is empty or contains only the header.'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': f'Error reading the file: {str(e)}'}, status=500)
        
    
        # Save the uploaded CSV file to the TimeSheetFile model
        timesheet_file = TimeSheetFile.objects.create(file=csv_file)

        # Trigger Celery task to process the CSV file asynchronously
        process_csv_file.delay(timesheet_file.id)
        
        # Return a JSON response with the file ID for status checking
        return JsonResponse(
            {
                'message': 'File uploaded successfully. Processing commenced.',
                'file_id': timesheet_file.id
            }
        )

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def upload_status(request, file_id):
    """
    Returns the processing status of the uploaded CSV file.
    """
    try:
        timesheet_file = TimeSheetFile.objects.get(id=file_id)
        
        if timesheet_file.status == Status.FAILED:
            return JsonResponse({'status': timesheet_file.status, 'message': timesheet_file.error_message})
        
        return JsonResponse({'status': timesheet_file.status})
    
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

