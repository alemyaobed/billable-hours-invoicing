# Generated by Django 4.2.16 on 2024-09-19 18:21

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillableRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoices.employee')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSheetFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='timesheets/')),
                ('is_fully_processed', models.BooleanField(default=False)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TimesheetInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('invoice_date', models.DateField(default=django.utils.timezone.now)),
                ('billable_rate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoices.billablerate')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoices.employee')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoices.timesheetfile')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoices.project')),
            ],
        ),
        migrations.DeleteModel(
            name='Timesheet',
        ),
        migrations.AddField(
            model_name='billablerate',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoices.timesheetfile'),
        ),
        migrations.AlterUniqueTogether(
            name='billablerate',
            unique_together={('file', 'employee')},
        ),
    ]
