from django.db import models
from datetime import datetime
from uuid import uuid4
from django.utils.timezone import now


class Status(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PROCESSED = 'PROCESSED', 'Processed'
    FAILED = 'FAILED', 'Failed'


class TimeSheetFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    file = models.FileField(upload_to='timesheets/')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    error_message = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class Employee(models.Model):
    employee_id = models.IntegerField(unique=True)


class BillableRate(models.Model):
    file = models.ForeignKey(TimeSheetFile, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('file', 'employee')


class Project(models.Model):
    name = models.CharField(max_length=255)


class TimesheetInvoice(models.Model):
    file = models.ForeignKey(TimeSheetFile, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    billable_rate = models.ForeignKey(BillableRate, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    invoice_date = models.DateField(default=now)

    @property
    def hours_worked(self):
        """Calculates total hours worked."""
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        duration = end - start
        return round(duration.total_seconds() / 3600, 2)


    def __str__(self):
        return f"TimesheetInvoice {self.id} - {self.employee} - {self.date}"
    

class InvoiceSummary(models.Model):
    file = models.ForeignKey(TimeSheetFile, on_delete=models.CASCADE)
    project_summary = models.JSONField()
    project_total_costs = models.JSONField()
    
    def __str__(self):
        return f"InvoiceSummary {self.id} - {self.file}"
