from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('invoices/<uuid:file_id>/', views.view_invoices, name='view_invoices'),
    path('status/<uuid:file_id>/', views.upload_status, name='upload_status'),
]
