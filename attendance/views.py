from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta, date
import json

from .models import Attendance, AttendanceActivity
from .forms import CheckInForm, CheckOutForm
from authentication.models import UserProfile


@login_required
def check_in_view(request):
    """Student check-in page"""
    # Get user profile
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Check if user is a student
    if not user_profile.is_student():
        messages.error(request, "Only students can check in to the library.")
        return redirect('main:mainpage')
    
    # Check if already checked in today
    today = timezone.now().date()
    active_attendance = Attendance.objects.filter(
        user=request.user,
        check_in_time__date=today,
        status='checked_in'
    ).first()
    
    if active_attendance:
        # Already checked in, show check-out option
        return redirect('attendance:active_attendance')
    
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.user = request.user
            attendance.save()
            form.save_m2m()
            
            messages.success(
                request,
                f"Welcome to the library! ✨ You checked in at {attendance.check_in_time.strftime('%H:%M')}"
            )
            return redirect('attendance:active_attendance')
    else:
        form = CheckInForm()
    
    # Get reading stats for gamification (if available)
    reading_stats = get_reading_stats(request.user)
    
    context = {
        'form': form,
        'user_profile': user_profile,
        'reading_stats': reading_stats,
    }
    
    return render(request, 'check-in.html', context)


@login_required
def active_attendance_view(request):
    """Show active attendance and provide check-out option"""
    today = timezone.now().date()
    
    # Get current active attendance
    active_attendance = Attendance.objects.filter(
        user=request.user,
        check_in_time__date=today,
        status='checked_in'
    ).first()
    
    if not active_attendance:
        messages.info(request, "You are not currently checked in.")
        return redirect('attendance:check_in')
    
    if request.method == 'POST':
        form = CheckOutForm(request.POST)
        if form.is_valid():
            active_attendance.check_out_time = timezone.now()
            active_attendance.status = 'checked_out'
            active_attendance.save()
            
            messages.success(
                request,
                f"Thank you for visiting! See you soon! 📚 "
                f"You spent {active_attendance.duration_display} in the library."
            )
            return redirect('attendance:check_in')
    else:
        form = CheckOutForm()
    
    # Calculate time spent
    time_spent = timezone.now() - active_attendance.check_in_time
    minutes_spent = int(time_spent.total_seconds() / 60)
    hours_spent = minutes_spent // 60
    remaining_minutes = minutes_spent % 60
    
    context = {
        'active_attendance': active_attendance,
        'form': form,
        'minutes_spent': minutes_spent,
        'hours_spent': hours_spent,
        'remaining_minutes': remaining_minutes,
    }
    
    return render(request, 'active-attendance.html', context)


@login_required
def dashboard_view(request):
    """Dashboard for librarian and teacher - real-time statistics"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Check if user has authorization
    if not user_profile.is_librarian() and not user_profile.is_teacher():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('main:mainpage')
    
    today = timezone.now().date()
    
    # Real-time statistics
    active_visitors = Attendance.objects.filter(
        check_in_time__date=today,
        status='checked_in'
    ).count()
    
    total_visitors_today = Attendance.objects.filter(
        check_in_time__date=today
    ).count()
    
    # Last 7 days trend
    week_ago = today - timedelta(days=6)
    daily_stats = []
    for i in range(7):
        current_date = week_ago + timedelta(days=i)
        count = Attendance.objects.filter(check_in_time__date=current_date).count()
        daily_stats.append({
            'date': current_date.strftime('%a'),
            'count': count
        })
    
    # Activity statistics
    activity_stats = []
    activities = AttendanceActivity.objects.filter(is_active=True)
    for activity in activities:
        count = Attendance.objects.filter(
            check_in_time__date=today,
            activities=activity
        ).count()
        if count > 0:
            activity_stats.append({
                'name': str(activity),
                'count': count
            })
    
    # Average visit duration today
    avg_duration = Attendance.objects.filter(
        check_in_time__date=today,
        status__in=['checked_out', 'auto_checked_out']
    ).aggregate(avg=Avg('duration_minutes'))
    avg_duration_display = "—"
    if avg_duration['avg']:
        avg_minutes = int(avg_duration['avg'])
        hours = avg_minutes // 60
        minutes = avg_minutes % 60
        if hours > 0:
            avg_duration_display = f"{hours}h {minutes}m"
        else:
            avg_duration_display = f"{minutes}m"
    
    # Get all active visitors with details
    active_visitor_list = Attendance.objects.select_related('user__profile').filter(
        check_in_time__date=today,
        status='checked_in'
    ).order_by('-check_in_time')
    
    # Monthly recap option
    if request.method == 'POST' and 'generate_monthly' in request.POST:
        month = request.POST.get('month')
        year = request.POST.get('year', str(today.year))
        # This is a placeholder for monthly report generation
        return monthly_report_view(request, int(year), int(month))
    
    context = {
        'active_visitors': active_visitor_list,
        'active_count': active_visitors,
        'total_count': total_visitors_today,
        'daily_stats': daily_stats,
        'activity_stats': activity_stats,
        'avg_duration': avg_duration_display,
        'user_profile': user_profile,
        'today': today,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def monthly_report_view(request, year, month):
    """Generate monthly attendance report"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if not user_profile.is_librarian() and not user_profile.is_teacher():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('main:mainpage')
    
    from calendar import monthrange
    
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    # Get all attendance records for the month
    monthly_records = Attendance.objects.filter(
        check_in_time__date__gte=first_day,
        check_in_time__date__lte=last_day
    ).select_related('user__profile')
    
    # Statistics
    total_unique_visitors = monthly_records.values('user').distinct().count()
    total_visits = monthly_records.count()
    avg_daily_visitors = total_unique_visitors / (last_day - first_day).days if (last_day - first_day).days > 0 else 0
    
    # Daily breakdown
    daily_breakdown = []
    for day in range(1, (last_day - first_day).days + 2):
        current_date = first_day + timedelta(days=day-1)
        day_records = monthly_records.filter(check_in_time__date=current_date)
        daily_breakdown.append({
            'date': current_date,
            'visitors': day_records.values('user').distinct().count(),
            'visits': day_records.count(),
        })
    
    # Top readers (most visits)
    top_students = monthly_records.values('user__first_name', 'user__last_name').annotate(
        visit_count=Count('id')
    ).order_by('-visit_count')[:10]
    
    context = {
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'total_unique_visitors': total_unique_visitors,
        'total_visits': total_visits,
        'avg_daily_visitors': round(avg_daily_visitors, 1),
        'daily_breakdown': daily_breakdown,
        'top_students': top_students,
        'records': monthly_records,
    }
    
    return render(request, 'monthly-report.html', context)


@require_http_methods(["POST"])
@login_required
def auto_checkout_view(request, record_id):
    """Force check-out for a specific attendance record (admin use)"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if not user_profile.is_librarian():
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    attendance = get_object_or_404(Attendance, id=record_id)
    
    if attendance.status == 'checked_in':
        attendance.check_out_time = timezone.now()
        attendance.status = 'checked_out'
        attendance.save()
        return JsonResponse({'status': 'success', 'duration': attendance.duration_display})
    
    return JsonResponse({'status': 'error', 'message': 'Already checked out'})


def get_reading_stats(user):
    """
    Placeholder for reading statistics
    This will be populated when reading tracker feature is implemented
    """
    # For now, return empty stats
    return {
        'books_read_this_month': 0,
        'reading_minutes_this_week': 0,
        'reading_streak': 0,
        'next_milestone': 5,  # Next goal: 5 books
        'message': 'Ready to read today?'
    }
