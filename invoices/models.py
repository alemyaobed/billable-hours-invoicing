from django.db import models
from datetime import date, datetime, timedelta

class Employee(models.Model):
    employee_id = models.IntegerField(unique=True)

class Project(models.Model):
    name = models.CharField(max_length=255)

class Timesheet(models.Model):
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
