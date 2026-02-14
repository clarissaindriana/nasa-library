from django.urls import path
from .views import (
    check_in_view,
    active_attendance_view,
    dashboard_view,
    monthly_report_view,
    auto_checkout_view,
    attendance_history_view,
)

app_name = 'attendance'

urlpatterns = [
    path('check-in/', check_in_view, name='check_in'),
    path('active/', active_attendance_view, name='active_attendance'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('report/<int:year>/<int:month>/', monthly_report_view, name='monthly_report'),
    path('auto-checkout/<int:record_id>/', auto_checkout_view, name='auto_checkout'),
    path('history/', attendance_history_view, name='history'),
]
