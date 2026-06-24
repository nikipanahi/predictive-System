from django.urls import path
from . import views # یعنی از همین پوشه فایل views را بیاور

urlpatterns = [
    path('api/sync/', views.export_for_offline, name='export_offline'),
]