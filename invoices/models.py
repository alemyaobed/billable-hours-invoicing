from django.db import models
from datetime import date, datetime, timedelta
from uuid import uuid4

class TimeSheetFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    file = models.FileField(upload_to='timesheets/')
    is_fully_processed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class Employee(models.Model):
    employee_id = models.IntegerField(unique=True)

class Project(models.Model):
    name = models.CharField(max_length=255)

class Timesheet(models.Model):
    file = models.ForeignKey(TimeSheetFile, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    billable_rate = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    @property
    def hours_worked(self):
        """Calculates total hours worked."""
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        duration = end - start
        return round(duration.total_seconds() / 3600, 2)

class Invoice(models.Model):
    file = models.ForeignKey(TimeSheetFile, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    number_of_hours = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_date = models.DateField(default=date.today)
    

    @property
    def total_amount(self):
        return self.timesheet.hours_worked * self.timesheet.billable_rate
