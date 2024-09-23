from django.urls import path
from .views import IndexView, UploadCSVView, InvoicesView, StatusView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('upload/', UploadCSVView.as_view(), name='upload_csv'),
    path('invoices/<uuid:file_id>/', InvoicesView.as_view(), name='view_invoices'),
    path('status/<uuid:file_id>/', StatusView.as_view(), name='upload_status'),
]
