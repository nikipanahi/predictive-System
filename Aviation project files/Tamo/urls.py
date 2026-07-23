from django.urls import path, include
from . import views
from django.contrib import admin
urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('inspection/add/', views.add_part, name='add_part'),
    path('delete/<int:pk>/', views.delete_part, name='delete_part'),
    path('part/<int:pk>/history/', views.part_history, name='part_history'),
    path('part/<int:pk>/edit/', views.edit_part, name='edit_part'),
    path('get-part-details/', views.get_part_details, name='get_part_details'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('export/excel/', views.export_inventory_excel, name='export_inventory_excel'),
    path('scanner/', views.inventory_scanner, name='inventory_scanner'),
    path('verify-qr/<int:pk>/', views.verify_qr_api, name='verify_qr_api'),
    path('audit-report/', views.inventory_audit_report, name='audit_report'),
    path('track-part/<str:part_no>/<str:serial_no>/', views.track_part_history, name='track_part_history'),
    path('toggle-audit/<int:pk>/', views.toggle_audit_status_ajax, name='toggle_audit_ajax'),
    path('part/<int:pk>/toggle-audit/', views.toggle_audit_status, name='toggle_audit'),
    path('inspection/check-history/', views.check_serial_history, name='check_serial_history'),
    path('part/<int:pk>/mark-repaired/', views.mark_as_repaired, name='mark_as_repaired'),
    path('part/<int:pk>/report-failure/', views.report_failure, name='report_failure'),
    path('api/sync/', views.export_for_offline, name='export_offline'),
]
