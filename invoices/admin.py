from django.contrib import admin
from .models import Employee, Project, TimesheetInvoice

admin.site.register(Employee)
admin.site.register(Project)
admin.site.register(TimesheetInvoice)
