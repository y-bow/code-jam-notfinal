from flask import Blueprint, render_template, session, request, redirect, url_for, g
from datetime import datetime
from middleware import school_scoped, role_minimum
from models import (
    db, User, Course, Enrollment, Assignment, Submission,
    Section, CustomTask, Announcement, TimetableEntry
)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/student')
@school_scoped
def student_dashboard():
    user = g.current_user
    today_classes = []
    
    current_day = datetime.now().weekday()
    if current_day <= 4:  # Monday to Friday
        if user.student_profile and user.student_profile.section_id:
            entries = TimetableEntry.query.filter_by(
                section_id=user.student_profile.section_id,
                day=current_day
            ).all()
            
            today_classes = [entry.to_dict() for entry in entries]
            # Sort by time
            today_classes.sort(key=lambda x: datetime.strptime(x['startTime'], '%I:%M %p').time() if 'AM' in x['startTime'] or 'PM' in x['startTime'] else x['startTime'])

    return render_template('dashboard/student_dashboard.html', today_classes=today_classes)


@dashboard_bp.route('/teacher')
@school_scoped
def teacher_dashboard():
    return render_template('dashboard/teacher_dashboard.html')


@dashboard_bp.route('/timetable')
@school_scoped
def timetable():
    user = g.current_user
    
    timetable_data = {}
    if user.student_profile and user.student_profile.section_id:
        entries = TimetableEntry.query.filter_by(
            section_id=user.student_profile.section_id
        ).all()
        
        # Group by day (0=Monday, 1=Tuesday, ...)
        for i in range(5):
            timetable_data[i] = []
            
        for entry in entries:
            # Simple sorting by start_time (assuming standard AM/PM format that sorts OK or we handle it in template)
            timetable_data[entry.day].append(entry.to_dict())
            
        # Optional: Sort entries by time within each day
        for day in timetable_data:
            timetable_data[day].sort(key=lambda x: datetime.strptime(x['startTime'], '%I:%M %p').time() if 'AM' in x['startTime'] or 'PM' in x['startTime'] else x['startTime'])
            
    # Calculate current day of week (0=Monday, 6=Sunday)
    current_day = datetime.now().weekday()
    # If it's weekend, we set it to something outside 0-4
    if current_day > 4:
        current_day = -1

    return render_template('dashboard/timetable.html', timetable_data=timetable_data, current_day=current_day)


@dashboard_bp.route('/tasks', methods=['GET', 'POST'])
@school_scoped
def tasks():
    user = g.current_user
    if request.method == 'POST':
        title = request.form.get('title')
        due_date_str = request.form.get('due_date')
        from datetime import datetime
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        new_task = CustomTask(user_id=user.id, title=title, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('dashboard.tasks'))

    custom_tasks = (
        CustomTask.query
        .filter_by(user_id=user.id)
        .order_by(CustomTask.is_completed, CustomTask.due_date.asc())
        .all()
    )
    custom_tasks.sort(key=lambda x: (x.is_completed, x.due_date is None, x.due_date))
    return render_template('dashboard/tasks.html', custom_tasks=custom_tasks)


@dashboard_bp.route('/tasks/toggle/<int:task_id>', methods=['POST'])
@school_scoped
def toggle_task(task_id):
    task = CustomTask.query.get_or_404(task_id)
    if task.user_id == g.current_user.id:
        task.is_completed = not task.is_completed
        db.session.commit()
    return redirect(url_for('dashboard.tasks'))


@dashboard_bp.route('/tasks/delete/<int:task_id>', methods=['POST'])
@school_scoped
def delete_task(task_id):
    task = CustomTask.query.get_or_404(task_id)
    if task.user_id == g.current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('dashboard.tasks'))


@dashboard_bp.route('/grades')
@school_scoped
def grades():
    return render_template('dashboard/grades.html')


@dashboard_bp.route('/announcements')
@school_scoped
def announcements():
    # School-scoped: only announcements from this school
    school_announcements = (
        Announcement.query
        .filter_by(school_id=g.school_id)
        .order_by(Announcement.posted_at.desc())
        .all()
    )
    return render_template('dashboard/announcements.html', announcements=school_announcements)


@dashboard_bp.route('/messages')
@school_scoped
def messages():
    return render_template('dashboard/messages.html')


# =============================================================================
# SCHOOL-SCOPED DATA QUERIES (example endpoints)
# =============================================================================

@dashboard_bp.route('/my-courses')
@school_scoped
def my_courses():
    """Fetch courses scoped by role and school."""
    user = g.current_user

    if user.role in ('student', 'class_rep'):
        courses = (
            Course.query
            .join(Enrollment, Enrollment.course_id == Course.id)
            .join(Section, Course.section_id == Section.id)
            .filter(
                Enrollment.student_id == user.id,
                Section.school_id == g.school_id
            )
            .all()
        )
    elif user.role in ('teacher', 'assistant'):
        courses = (
            Course.query
            .join(Section)
            .filter(
                Course.teacher_id == user.id,
                Section.school_id == g.school_id
            )
            .all()
        )
    elif user.role in ('dean', 'timetable_manager'):
        courses = (
            Course.query
            .join(Section)
            .filter(Section.school_id == g.school_id)
            .all()
        )
    else:
        courses = []

    return render_template('dashboard/courses.html', courses=courses)


@dashboard_bp.route('/analytics')
@school_scoped
@role_minimum('dean')
def school_analytics():
    """Dean-only: analytics scoped to their school."""
    total_students = User.query.filter_by(school_id=g.school_id, role='student').count()
    total_teachers = User.query.filter_by(school_id=g.school_id, role='teacher').count()
    total_sections = Section.query.filter_by(school_id=g.school_id).count()
    total_courses = (
        Course.query
        .join(Section)
        .filter(Section.school_id == g.school_id)
        .count()
    )

    return render_template('dashboard/analytics.html',
                           total_students=total_students,
                           total_teachers=total_teachers,
                           total_sections=total_sections,
                           total_courses=total_courses)
