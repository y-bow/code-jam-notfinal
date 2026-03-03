from flask import Blueprint, render_template, session, request, redirect, url_for
from auth import login_required, role_required
from models import User, Course, Enrollment, Assignment, Submission, db, CustomTask

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/student')
@login_required
@role_required('student')
def student_dashboard():
    # In a full app, we would query the db for the student's actual timetable, assignments, etc.
    # user_id = session.get('user_id')
    # enrollments = Enrollment.query.filter_by(student_id=user_id).all()
    # ...
    return render_template('dashboard/student_dashboard.html')

@dashboard_bp.route('/teacher')
@login_required
@role_required('teacher')
def teacher_dashboard():
    # In a full app, we would query the db for the teacher's courses, student metrics, etc.
    # user_id = session.get('user_id')
    # courses = Course.query.filter_by(teacher_id=user_id).all()
    # ...
    return render_template('dashboard/teacher_dashboard.html')

@dashboard_bp.route('/timetable')
@login_required
def timetable():
    return render_template('dashboard/timetable.html')

@dashboard_bp.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    user_id = session.get('user_id')
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
        
        new_task = CustomTask(user_id=user_id, title=title, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('dashboard.tasks'))
        
    custom_tasks = CustomTask.query.filter_by(user_id=user_id).order_by(CustomTask.is_completed, CustomTask.due_date.asc()).all()
    # Handle NULL due_date sorting in Python to avoid SQLite limitations
    custom_tasks.sort(key=lambda x: (x.is_completed, x.due_date is None, x.due_date))
    return render_template('dashboard/tasks.html', custom_tasks=custom_tasks)

@dashboard_bp.route('/tasks/toggle/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = CustomTask.query.get_or_404(task_id)
    if task.user_id == session.get('user_id'):
        task.is_completed = not task.is_completed
        db.session.commit()
    return redirect(url_for('dashboard.tasks'))

@dashboard_bp.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = CustomTask.query.get_or_404(task_id)
    if task.user_id == session.get('user_id'):
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('dashboard.tasks'))

@dashboard_bp.route('/grades')
@login_required
def grades():
    return render_template('dashboard/grades.html')

@dashboard_bp.route('/announcements')
@login_required
def announcements():
    return render_template('dashboard/announcements.html')

@dashboard_bp.route('/messages')
@login_required
def messages():
    return render_template('dashboard/messages.html')
