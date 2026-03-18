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

    elif user.role in ('teacher', 'assistant', 'dean', 'timetable_manager', 'admin', 'superadmin'):
        # Verify teacher owns the course or user is an admin/dean
        if user.role in ('teacher', 'assistant') and course.teacher_id != user.id:
            flash('Access Denied: This is not your course.', 'danger')
            return redirect(url_for('dashboard.teacher_dashboard'))
            
        from ..models import Grade, Attendance, Announcement, Assignment, db
        from datetime import date
        
        students_data = []
        for enrollment in course.enrollments:
            student_user = enrollment.student
            grade_record = Grade.query.filter_by(student_id=student_user.id, course_id=course.id).first()
            grade_val = grade_record.grade if grade_record else 0.0
            
            total_classes = Attendance.query.filter_by(course_id=course.id, student_id=student_user.id).count()
            present_classes = Attendance.query.filter_by(course_id=course.id, student_id=student_user.id, status='present').count()
            attendance_perc = (present_classes / total_classes * 100) if total_classes > 0 else 100.0
            
            risk = 'high' if (attendance_perc < 75 or grade_val < 50.0) else 'low'
            
            students_data.append({
                'id': student_user.id,
                'name': student_user.name,
                'email': student_user.email,
                'attendance': round(attendance_perc, 1),
                'grade': round(grade_val, 2),
                'risk': risk
            })
        
        assignments = course.assignments.all()
        announcements = course.announcements.order_by(Announcement.posted_at.desc()).all()

        return render_template('classroom/teacher_view.html', 
                               course=course,
                               students=students_data,
                               assignments=assignments,
                               announcements=announcements,
                               today_date=date.today().strftime('%Y-%m-%d'))

    return redirect(url_for('index'))


from flask import request
from datetime import datetime

@classroom_bp.route('/<int:course_id>/update_grade', methods=['POST'])
@school_scoped
def update_grade(course_id):
    user = g.current_user
    course = Course.query.get_or_404(course_id)
    owns_resource(course.section, 'school_id')
    
    if user.role not in ('teacher', 'dean', 'admin', 'superadmin'):
        flash('Access Denied: Insufficient permissions to edit grades.', 'danger')
        return redirect(url_for('classroom.view_classroom', course_id=course_id))

    if user.role == 'teacher' and course.teacher_id != user.id:
        flash('Access Denied: You can only edit grades for your own courses.', 'danger')
        return redirect(url_for('classroom.view_classroom', course_id=course_id))

    student_id = request.form.get('student_id', type=int)
    grade_val = request.form.get('grade', type=float)
    
    if student_id and grade_val is not None:
        from ..models import Grade, db
        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course.id).first()
        if enrollment:
            grade_record = Grade.query.filter_by(student_id=student_id, course_id=course.id).first()
            if grade_record:
                grade_record.grade = grade_val
                grade_record.calculated_at = datetime.utcnow()
            else:
                grade_record = Grade(student_id=student_id, course_id=course.id, grade=grade_val)
                db.session.add(grade_record)
            db.session.commit()
            flash('Grade updated successfully.', 'success')
        else:
            flash('Student not found in this course.', 'danger')
            
    return redirect(url_for('classroom.view_classroom', course_id=course_id))
