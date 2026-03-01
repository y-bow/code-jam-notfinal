from flask import Blueprint, render_template, session, flash, redirect, url_for
from auth import login_required
from models import Course, Enrollment

classroom_bp = Blueprint('classroom', __name__, url_prefix='/classroom')

@classroom_bp.route('/<int:course_id>')
@login_required
def view_classroom(course_id):
    user_id = session.get('user_id')
    role = session.get('role')
    
    # Verify access
    if role == 'student':
        # Check if student is enrolled
        # enrollment = Enrollment.query.filter_by(student_id=user_id, course_id=course_id).first()
        # if not enrollment:
        #    flash("Access Denied", "danger")
        #    return redirect(url_for('dashboard.student_dashboard'))
        return render_template('classroom/student_view.html')
        
    elif role == 'teacher':
        # Check if teacher owns the course
        # course = Course.query.get(course_id)
        # if not course or course.teacher_id != user_id:
        #    flash("Access Denied", "danger")
        #    return redirect(url_for('dashboard.teacher_dashboard'))
        return render_template('classroom/teacher_view.html')
        
    return redirect(url_for('index'))
