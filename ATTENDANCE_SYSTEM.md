# Library Attendance System - Setup Guide

## Overview

This is a comprehensive library attendance/check-in system for SMAN 61 Jakarta with role-based features:

- **Students**: Check-in, record activities, check-out, gamified reading tracker
- **Teachers & Librarians**: Real-time dashboard, statistics, monthly reports

## Features

### 1. Student Check-In System
- ✅ Auto-record entry time, name, role
- ✅ Select/input activities (reading, doing homework, borrowing books, etc.)
- ✅ Gamification elements with reading tracker integration
- ✅ Elegant, modern UI matching the app theme

### 2. Check-Out System
- ✅ Manual check-out with confirmation
- ✅ Auto check-out at 3:00 PM (closing time)
- ✅ Duration calculation
- ✅ Activity history display

### 3. Librarian/Teacher Dashboard
- ✅ Real-time active visitors count
- ✅ Total daily visitors
- ✅ Average visit duration
- ✅ Activity statistics
- ✅ Weekly trend chart
- ✅ Active visitor list with details

### 4. Monthly Reports
- ✅ Total unique visitors
- ✅ Total visits
- ✅ Daily breakdown
- ✅ Top 10 students
- ✅ Printable for accreditation

## Installation & Setup

### 1. Run Migrations
```bash
python manage.py migrate attendance
```

### 2. Initialize Default Activities
```bash
python manage.py init_activities
```

This will create 8 default activities:
- 📚 Reading Books
- 📝 Doing Homework
- 🤝 Borrowing Books
- 🔍 Research
- 👥 Group Study
- 📰 Reading Magazines
- 💻 Computer Work
- 🤫 Quiet Time

### 3. Create Superuser (if not already done)
```bash
python manage.py createsuperuser
```

### 4. Access Admin Panel
- Go to `/admin/` and log in
- Configure activities, add more as needed
- Monitor attendance records

## URLs

### Student URLs
- `/attendance/check-in/` - Check-in page
- `/attendance/active/` - Active session view (check-out)

### Staff URLs
- `/attendance/dashboard/` - Real-time dashboard
- `/attendance/report/<year>/<month>/` - Monthly report

## Models

### AttendanceActivity
- name: Activity name (e.g., "Reading Books")
- emoji: Emoji icon
- description: Activity description
- is_active: Whether it's available for selection
- order: Display order

### Attendance
- user: Foreign key to User
- check_in_time: Auto-recorded entry time
- check_out_time: Recorded/auto-recorded exit time
- status: checked_in, checked_out, auto_checked_out
- activities: M2M with AttendanceActivity
- custom_activity: Free-text activity field
- duration_minutes: Auto-calculated visit duration

## Role-Based Access Control

### Students
- Can check-in and check-out
- View their own attendance history
- See reading tracker stats
- Can't access dashboard or reports

### Teachers
- Can view real-time dashboard
- Can see all active visitors
- Can generate monthly reports
- Can force check-out if needed

### Librarians
- Can manage activities (admin)
- Can view real-time dashboard
- Can see all active visitors
- Can force check-out if needed
- Can generate monthly reports
- Can access full admin interface

## Frontend Integration

### Navbar Updates
The navbar has been updated to include:
- **Students**: Link to check-in page (📍 Check-in)
- **Teachers/Librarians**: Link to dashboard (📊 Dashboard)

Links appear in both desktop and mobile menus.

## Gamification Features

The check-in page includes:
- 🔥 Reading streak counter
- 📊 Books read this month
- 📈 Progress towards next milestone
- 💡 Motivational messages
- Future integration with reading tracker

## Auto Check-Out Feature

The system includes auto check-out functionality at 3:00 PM:
- Students are informed during check-in
- Can enable via background task/cron job:

```python
# In settings.py, add:
CELERY_BEAT_SCHEDULE = {
    'auto-checkout-3pm': {
        'task': 'attendance.tasks.auto_checkout_at_closing',
        'schedule': crontab(hour=15, minute=0),  # 3:00 PM
    },
}
```

## Customization

### Change Closing Time
Edit in `views.py`, function `check_in_view`:
```python
# Current: 15:00 (3:00 PM)
# Change auto_checked_out logic to different time
```

### Add More Activities
1. **Via Django Admin**: Go to `/admin/attendance/attendanceactivity/`
2. **Via Management Command**: Create new activity in migration

### Modify Design
All templates are in `/attendance/templates/`:
- `check-in.html` - Student check-in
- `active-attendance.html` - Active session
- `dashboard.html` - Real-time dashboard
- `monthly-report.html` - Monthly report

## API Endpoints

### Auto Checkout (Librarian)
```
POST /attendance/auto-checkout/<record_id>/
```

Response:
```json
{
    "status": "success",
    "duration": "1h 30m"
}
```

## Admin Features

1. **Attendance Activity Admin**
   - Create/edit/delete activities
   - Set display order
   - Enable/disable activities

2. **Attendance Admin**
   - View all attendance records
   - Filter by status, date, activities
   - Search by student name
   - Sort by date
   - Mark multiple records as checked out
   - Prevent accidental deletion (superuser only)

## Security

- ✅ Login required for all views
- ✅ Role-based access control enforced
- ✅ CSRF token protection
- ✅ User data protection
- ✅ Admin actions restricted to librarians

## Future Enhancements

- [ ] Mobile app native check-in
- [ ] NFC/RFID card scanning
- [ ] Facial recognition
- [ ] Reading tracker integration (award badges)
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Export to Excel/PDF
- [ ] Attendance analytics charts
- [ ] Parent notifications
- [ ] Student milestone celebrations

## Troubleshooting

### Models not appearing in admin
- Run: `python manage.py migrate`
- Check INSTALLED_APPS includes 'attendance'

### Activities not showing
- Run: `python manage.py init_activities`
- Check is_active field in admin

### Navbar links not working
- Verify URLs are correctly configured
- Check user.profile attribute exists
- Ensure UserProfile.role values are correct

### Dashboard showing no data
- Make sure attendance records exist for today
- Check system time/timezone settings
- Verify user has correct role

## Support

For issues or feature requests:
1. Check the logs: `tail -f logs/django.log`
2. Review migrations: `python manage.py showmigrations`
3. Check user roles in admin
4. Verify database structure: `python manage.py sqlmigrate attendance 0001`

## Files Created/Modified

### New Files
- `attendance/models.py` - Model definitions
- `attendance/forms.py` - Check-in/check-out forms
- `attendance/views.py` - All view logic
- `attendance/urls.py` - URL routing
- `attendance/admin.py` - Admin interface
- `attendance/management/commands/init_activities.py` - Setup command
- `attendance/templates/check-in.html` - Student check-in page
- `attendance/templates/active-attendance.html` - Active session page
- `attendance/templates/dashboard.html` - Staff dashboard
- `attendance/templates/monthly-report.html` - Monthly report

### Modified Files
- `nasa_library/settings.py` - Added 'attendance' to INSTALLED_APPS
- `nasa_library/urls.py` - Added attendance URL include
- `templates/navbar.html` - Added check-in/dashboard links

## Responsive Design

- ✅ Mobile-first approach
- ✅ Tablet optimized
- ✅ Desktop enhanced
- ✅ Touch-friendly buttons
- ✅ Accessible forms
- ✅ Print-friendly reports

---

**Version**: 1.0  
**Last Updated**: February 14, 2026  
**Status**: Ready for Production
