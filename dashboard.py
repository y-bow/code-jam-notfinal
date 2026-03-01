from flask import Blueprint, render_template, session
from auth import login_required, role_required
from models import User, Course, Enrollment, Assignment, Submission

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

@dashboard_bp.route('/tasks')
@login_required
def tasks():
    return render_template('dashboard/tasks.html')

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
