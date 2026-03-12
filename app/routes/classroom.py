from flask import Blueprint, render_template, g, flash, redirect, url_for
from ..middleware import school_scoped, owns_resource
from ..models import Course, Enrollment, Section

classroom_bp = Blueprint('classroom', __name__, url_prefix='/classroom')


@classroom_bp.route('/<int:course_id>')
@school_scoped
def view_classroom(course_id):
    user = g.current_user

    # Load course and verify it belongs to this school
    course = Course.query.get_or_404(course_id)
    owns_resource(course.section, 'school_id')

    if user.role in ('student', 'class_rep'):
        # Verify enrollment
        enrollment = Enrollment.query.filter_by(
            student_id=user.id, course_id=course_id
        ).first()
        if not enrollment:
            flash('Access Denied: You are not enrolled in this course.', 'danger')
            return redirect(url_for('dashboard.student_dashboard'))
        return render_template('classroom/student_view.html', course=course)

    elif user.role in ('teacher', 'assistant'):
        # Verify teacher owns the course
        if course.teacher_id != user.id:
            flash('Access Denied: This is not your course.', 'danger')
            return redirect(url_for('dashboard.teacher_dashboard'))
        return render_template('classroom/teacher_view.html', course=course)

    elif user.role in ('dean', 'timetable_manager'):
        # Dean/manager can view any course in their school
        return render_template('classroom/teacher_view.html', course=course)

    return redirect(url_for('index'))
