from flask import Blueprint, render_template, g, flash, redirect, url_for, abort, request
from ..middleware import school_scoped, owns_resource, role_minimum
from ..models import (
    db, User, Student, Course, Enrollment, Section, ProfessorAssistant, 
    ClassRepNomination, Announcement, ROLE_HIERARCHY, Assignment, Attendance, Submission, TeacherRating, JoinCode
)
from datetime import datetime

classroom_bp = Blueprint('classroom', __name__, url_prefix='/classroom')


@classroom_bp.route('/<int:course_id>')
@school_scoped
def view_classroom(course_id):
    user = g.current_user

    # Load course and verify it belongs to this school
    course = Course.query.get_or_404(course_id)
    owns_resource(course.section, 'school_id')

    # Fetch related data
    assignments = course.assignments.order_by(Assignment.due_date.desc()).all()
    announcements = course.announcements.order_by(Announcement.posted_at.desc()).all()
    
    # Enrich student data for the roster
    students_list = []
    for e in course.enrollments.all():
        s = e.student
        # Attach mock/calculated stats to avoid 500 in template
        # In a real app, these would come from Grade/Attendance models
        s.attendance = 85 # Placeholder
        s.grade = "A"     # Placeholder
        s.risk = "low"    # Placeholder
        students_list.append(s)

    today_date = datetime.now().strftime('%Y-%m-%d')

    if user.role in ('student', 'class_rep'):
        # Verify enrollment
        enrollment = Enrollment.query.filter_by(
            student_id=user.id, course_id=course_id
        ).first()
        if not enrollment:
            flash('Access Denied: You are not enrolled in this course.', 'danger')
            return redirect(url_for('dashboard.student_dashboard'))
        
        # Check if they are the Class Rep for this section/course
        is_cr = False
        if user.role == 'class_rep':
            nom = ClassRepNomination.query.filter_by(
                student_id=user.id, section_id=course.section_id, status='approved'
            ).first()
            is_cr = (nom is not None)

        return render_template('classroom/student_view.html', 
                               course=course, is_cr=is_cr, 
                               assignments=assignments, 
                               announcements=announcements,
                               students=students_list,
                               today_date=today_date)

    elif user.role == 'assistant_professor':
        # Verify they are assigned to THIS course
        pa_record = ProfessorAssistant.query.filter_by(
            course_id=course_id, assistant_teacher_id=user.id, is_active=True
        ).first()
        if not pa_record:
            flash('Access Denied: You are not an assistant for this course.', 'danger')
            return redirect(url_for('dashboard.teacher_dashboard'))
        return render_template('classroom/teacher_view.html', 
                               course=course, is_pa=True,
                               students=students_list,
                               assignments=assignments,
                               announcements=announcements,
                               today_date=today_date)

    elif user.role == 'professor':
        if course.teacher_id != user.id:
            flash('Access Denied: This is not your course.', 'danger')
            return redirect(url_for('dashboard.teacher_dashboard'))
        return render_template('classroom/teacher_view.html', 
                               course=course, is_pa=False,
                               students=students_list,
                               assignments=assignments,
                               announcements=announcements,
                               today_date=today_date)

    elif user.role == 'dean':
        return render_template('classroom/teacher_view.html', 
                               course=course, is_dean=True,
                               students=students_list,
                               assignments=assignments,
                               announcements=announcements,
                               today_date=today_date)
    
    elif user.role == 'admin':
        return render_template('classroom/teacher_view.html', 
                               course=course, is_admin=True,
                               students=students_list,
                               assignments=assignments,
                               announcements=announcements,
                               today_date=today_date)

    return redirect(url_for('index'))


@classroom_bp.route('/<int:course_id>/nominate_cr/<int:student_id>', methods=['POST'])
@school_scoped
@role_minimum('professor')
def nominate_class_rep(course_id, student_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != g.current_user.id:
        abort(403)
    
    # Check if student is enrolled
    enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if not enrollment:
        flash('Student is not enrolled in this course.', 'danger')
        return redirect(url_for('classroom.view_classroom', course_id=course_id))

    # Check for existing pending/approved nomination
    existing = ClassRepNomination.query.filter_by(
        section_id=course.section_id, status='approved'
    ).first()
    if existing:
        flash('This section already has an approved Class Representative.', 'warning')
        return redirect(url_for('classroom.view_classroom', course_id=course_id))

    nomination = ClassRepNomination(
        student_id=student_id,
        course_id=course_id,
        section_id=course.section_id,
        nominated_by=g.current_user.id,
        status='pending'
    )
    db.session.add(nomination)
    db.session.commit()
    
    flash('Class Rep nomination sent to Dean for approval.', 'success')
    return redirect(url_for('classroom.view_classroom', course_id=course_id))


@classroom_bp.route('/<int:course_id>/assign_assistant', methods=['POST'])
@school_scoped
@role_minimum('professor')
def assign_assistant_professor(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != g.current_user.id:
        abort(403)
    
    email = request.form.get('email')
    assistant = User.query.filter_by(school_id=g.school_id, email=email, role='professor').first()
    
    if not assistant:
        flash('Professor account not found with that email.', 'danger')
        return redirect(url_for('classroom.view_classroom', course_id=course_id))

    # Update their role to assistant_professor
    assistant.role = 'assistant_professor'
    
    pa_record = ProfessorAssistant(
        course_id=course_id,
        professor_id=g.current_user.id,
        assistant_teacher_id=assistant.id,
        is_active=True
    )
    db.session.add(pa_record)
    db.session.commit()
    
    flash(f'{assistant.name} has been assigned as an assistant for this course.', 'success')
    return redirect(url_for('classroom.view_classroom', course_id=course_id))


@classroom_bp.route('/<int:course_id>/create_assignment', methods=['POST'])
@school_scoped
@role_minimum('assistant_professor')
def create_assignment(course_id):
    course = Course.query.get_or_404(course_id)
    # Check if professor owns course or is Assistant Professor
    is_pa = False
    if g.current_user.role == 'assistant_professor':
        is_pa = ProfessorAssistant.query.filter_by(
            course_id=course_id, assistant_teacher_id=g.current_user.id, is_active=True
        ).first() is not None
    
    if course.teacher_id != g.current_user.id and not is_pa:
        abort(403)
        
    assignment = Assignment(
        course_id=course_id,
        title=request.form.get('title'),
        description=request.form.get('description'),
        due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%dT%H:%M'),
        points=int(request.form.get('points', 100))
    )
    db.session.add(assignment)
    db.session.commit()
    flash('Assignment posted successfully.', 'success')
    return redirect(url_for('classroom.view_classroom', course_id=course_id))


@classroom_bp.route('/<int:course_id>/mark_attendance', methods=['POST'])
@school_scoped
@role_minimum('assistant_professor')
def mark_attendance(course_id):
    course = Course.query.get_or_404(course_id)
    # Authorization same as above
    if course.teacher_id != g.current_user.id and g.current_user.role != 'assistant_professor':
        abort(403)
        
    date_str = request.form.get('date')
    att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    statuses = request.form.getlist('status')
    for s in statuses:
        student_id, status = s.split(':')
        # Check if record exists
        existing = Attendance.query.filter_by(
            course_id=course_id, student_id=student_id, date=att_date
        ).first()
        if existing:
            existing.status = status
        else:
            new_att = Attendance(
                course_id=course_id,
                student_id=student_id,
                date=att_date,
                status=status
            )
            db.session.add(new_att)
            
    db.session.commit()
    flash('Attendance saved successfully.', 'success')
    return redirect(url_for('classroom.view_classroom', course_id=course_id))


@classroom_bp.route('/<int:course_id>/post_announcement', methods=['POST'])
@school_scoped
def post_announcement(course_id):
    course = Course.query.get_or_404(course_id)
    user = g.current_user
    
    # Check if professor/Assistant Professor or Admin/Dean
    is_authorized = False
    if user.role in ('professor', 'admin', 'dean'):
        if user.role == 'professor' and course.teacher_id != user.id:
            pass # wait for Assistant Professor check
        else:
            is_authorized = True
    
    if not is_authorized and user.role == 'assistant_professor':
        is_authorized = ProfessorAssistant.query.filter_by(
            course_id=course_id, assistant_teacher_id=user.id, is_active=True
        ).first() is not None
        
    if not is_authorized and user.role == 'class_rep':
        # CR can only post to their own section for this course
        is_authorized = ClassRepNomination.query.filter_by(
            student_id=user.id, section_id=course.section_id, status='approved'
        ).first() is not None
        
    if not is_authorized:
        abort(403)
        
    new_ann = Announcement(
        school_id=g.school_id,
        course_id=course_id,
        section_id=course.section_id,
        teacher_id=user.id,
        title=request.form.get('title'),
        body=request.form.get('body'),
        urgent='urgent' in request.form
    )
    db.session.add(new_ann)
    db.session.commit()
    flash('Announcement posted.', 'success')
    return redirect(url_for('classroom.view_classroom', course_id=course_id))


@classroom_bp.route('/<int:course_id>/rate', methods=['POST'])
@school_scoped
@role_minimum('student')
def submit_rating(course_id):
    course = Course.query.get_or_404(course_id)
    rating_val = request.form.get('rating', type=int)
    review = request.form.get('review', '')
    is_anon = 'anonymous' in request.form
    
    if not rating_val or not (1 <= rating_val <= 5):
        flash('Invalid rating.', 'danger')
        return redirect(url_for('classroom.view_classroom', course_id=course_id))
        
    rating = TeacherRating(
        teacher_id=course.teacher_id,
        course_id=course_id,
        student_id=g.current_user.id,
        rating=rating_val,
        review=review,
        is_anonymous=is_anon
    )
    db.session.add(rating)
    db.session.commit()
    flash('Thank you for your feedback!', 'success')
    return redirect(url_for('classroom.view_classroom', course_id=course_id))


@classroom_bp.route('/join', methods=['POST'])
@school_scoped
@role_minimum('student')
def join_class():
    code_text = request.form.get('code', '').strip().upper()
    user = g.current_user

    if not code_text or len(code_text) != 6:
        flash('Invalid code format. Code must be 6 characters.', 'danger')
        return redirect(url_for('dashboard.student_dashboard'))

    # Validation: Code exists in JoinCode table
    join_code = JoinCode.query.filter_by(code=code_text).first()

    if not join_code:
        flash('Invalid or expired code.', 'danger')
        return redirect(url_for('dashboard.student_dashboard'))

    # Validation: is_active == True
    if not join_code.is_active:
        flash('Invalid or expired code.', 'danger')
        return redirect(url_for('dashboard.student_dashboard'))

    # Validation: expires_at > now
    if join_code.expires_at < datetime.utcnow():
        flash('Invalid or expired code.', 'danger')
        return redirect(url_for('dashboard.student_dashboard'))

    # Validation: use_count < max_uses (if max_uses set)
    if join_code.max_uses and join_code.use_count >= join_code.max_uses:
        flash('Invalid or expired code.', 'danger')
        return redirect(url_for('dashboard.student_dashboard'))

    # Validation: Student's school_id matches code's school_id
    if user.school_id != join_code.school_id:
        flash('This class is from a different university.', 'danger')
        return redirect(url_for('dashboard.student_dashboard'))

    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        student_id=user.id, course_id=join_code.course_id
    ).first()
    if existing_enrollment:
        flash('You are already enrolled in this class.', 'warning')
        return redirect(url_for('classroom.view_classroom', course_id=join_code.course_id))

    # On success: Create Enrollment record
    new_enrollment = Enrollment(
        student_id=user.id,
        course_id=join_code.course_id,
        status='active'
    )
    db.session.add(new_enrollment)

    # Increment JoinCode.use_count
    join_code.use_count += 1
    
    db.session.commit()

    # Redirect to classroom
    flash(f"Successfully joined {join_code.course.name}!", 'success')
    return redirect(url_for('classroom.view_classroom', course_id=join_code.course_id))
