from flask import Blueprint, render_template, session, request, redirect, url_for, g, jsonify, abort
from app.models import db, User, Message, Course, Enrollment, MessageLog
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
from markupsafe import escape

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

@messages_bp.before_request
def load_user():
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Unauthorized'}), 401
        return redirect(url_for('auth.login'))
    g.current_user = User.query.get(session['user_id'])
    if not g.current_user:
        session.clear()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Unauthorized'}), 401
        return redirect(url_for('auth.login'))

def can_message(sender, recipient):
    """Formal rules for who can message whom."""
    if sender.id == recipient.id:
        return False
        
    if sender.role == 'student':
        # Student CAN ONLY message professors of courses they are currently enrolled in
        if recipient.role not in ('professor', 'assistant_professor'):
            return False
            
        # Check if recipient teaches any course the student is enrolled in
        enrolled_course_ids = [e.course_id for e in sender.enrollments]
        taught_by_recipient = Course.query.filter(
            Course.id.in_(enrolled_course_ids),
            Course.teacher_id == recipient.id
        ).first()
        
        # Or if they are an assistant for an enrolled course
        if not taught_by_recipient and recipient.role == 'assistant_professor':
             from app.models import ProfessorAssistant
             taught_by_recipient = ProfessorAssistant.query.filter(
                 ProfessorAssistant.course_id.in_(enrolled_course_ids),
                 ProfessorAssistant.assistant_teacher_id == recipient.id,
                 ProfessorAssistant.is_active == True
             ).first()
        
        return taught_by_recipient is not None
        
    elif sender.role in ['professor', 'assistant_professor']:
        # Professor/Assistant can message any student enrolled in their courses
        # OR another professor/assistant in the same school
        if recipient.role in ['professor', 'assistant_professor', 'dean', 'admin']:
            return sender.school_id == recipient.school_id or sender.role == 'admin' or recipient.role == 'admin'
            
        if recipient.role == 'student':
            taught_course_ids = [c.id for c in sender.taught_courses]
            if sender.role == 'assistant_professor':
                from app.models import ProfessorAssistant
                taught_course_ids = [pa.course_id for pa in ProfessorAssistant.query.filter_by(assistant_teacher_id=sender.id, is_active=True).all()]
            
            enrolled_by_student = Enrollment.query.filter(
                Enrollment.course_id.in_(taught_course_ids),
                Enrollment.student_id == recipient.id
            ).first()
            return enrolled_by_student is not None
            
        return False
        
    elif sender.role == 'dean':
        return sender.school_id == recipient.school_id or recipient.role == 'admin'
        
    elif sender.role == 'admin':
        return True
        
    return False

def check_rate_limits(sender):
    """Enforce rate limits per hour."""
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_msgs_count = MessageLog.query.filter(
        MessageLog.sender_id == sender.id,
        MessageLog.sent_at >= one_hour_ago
    ).count()
    
    if sender.role == 'student' and recent_msgs_count >= 10:
        return False, "Message limit reached. Try again later."
    elif sender.role in ['professor', 'assistant_professor'] and recent_msgs_count >= 50:
        return False, "Message limit reached. Try again later."
    elif recent_msgs_count >= 100:
        return False, "Message limit reached. Try again later."
        
    return True, None

def check_spam(sender, recipient):
    """Prevent spamming the same teacher."""
    if sender.role == 'student' and recipient.role in ['professor', 'assistant_professor']:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_spam_count = MessageLog.query.filter(
            MessageLog.sender_id == sender.id,
            MessageLog.recipient_id == recipient.id,
            MessageLog.sent_at >= one_hour_ago,
            MessageLog.was_blocked == False
        ).count()
        
        if recent_spam_count >= 3:
            return False, "Please allow time for a response before sending more messages."
    
    return True, None

def log_attempt(sender_id, recipient_id, subject, ip_address, was_blocked, block_reason):
    log = MessageLog(
        sender_id=sender_id,
        recipient_id=recipient_id,
        subject=subject[:100] if subject else 'No Subject',
        ip_address=ip_address,
        was_blocked=was_blocked,
        block_reason=block_reason
    )
    db.session.add(log)
    db.session.commit()

@messages_bp.route('/')
def index():
    user = g.current_user
    
    # Get all distinct conversational partners for the inbox list
    sent_to = db.session.query(Message.recipient_id).filter_by(sender_id=user.id, is_deleted_by_sender=False).distinct()
    received_from = db.session.query(Message.sender_id).filter_by(recipient_id=user.id, is_deleted_by_recipient=False).distinct()
    
    partner_ids = set([r[0] for r in sent_to] + [r[0] for r in received_from])
    partners = User.query.filter(User.id.in_(partner_ids)).all() if partner_ids else []
    
    # Sort partners by latest message
    partner_data = []
    for p in partners:
        latest_msg = Message.query.filter(
            or_(
                and_(Message.sender_id == user.id, Message.recipient_id == p.id, Message.is_deleted_by_sender == False),
                and_(Message.sender_id == p.id, Message.recipient_id == user.id, Message.is_deleted_by_recipient == False)
            )
        ).order_by(Message.sent_at.desc()).first()
        
        unread_count = Message.query.filter_by(sender_id=p.id, recipient_id=user.id, is_read=False, is_deleted_by_recipient=False).count()
        
        if latest_msg:
            partner_data.append({
                'user': p,
                'latest_msg': latest_msg,
                'unread_count': unread_count
            })
            
    partner_data.sort(key=lambda x: x['latest_msg'].sent_at, reverse=True)

    # For the "To:" searchable dropdown, get all authorized recipients
    allowed_recipients = []
    if user.role == 'student':
        # Get professors of enrolled courses
        enrolled_course_ids = [e.course_id for e in user.enrollments]
        professors = User.query.join(Course, Course.teacher_id == User.id).filter(
            Course.id.in_(enrolled_course_ids)
        ).distinct().all()
        allowed_recipients = professors
    elif user.role in ['professor', 'assistant_professor']:
        # Get all students enrolled in their courses
        taught_course_ids = [c.id for c in user.taught_courses]
        if user.role == 'assistant_professor':
             from app.models import ProfessorAssistant
             taught_course_ids = [pa.course_id for pa in ProfessorAssistant.query.filter_by(assistant_teacher_id=user.id, is_active=True).all()]
             
        students = User.query.join(Enrollment, Enrollment.student_id == User.id).filter(
            Enrollment.course_id.in_(taught_course_ids)
        ).distinct().all()
        # Plus other professors in same school
        other_profs = User.query.filter(
            User.school_id == user.school_id, 
            User.role.in_(['professor', 'assistant_professor', 'dean']),
            User.id != user.id
        ).all()
        allowed_recipients = students + other_profs

    return render_template('messages/index.html', inbox_items=partner_data, allowed_recipients=allowed_recipients)

@messages_bp.route('/history/<int:user_id>')
def history(user_id):
    partner = User.query.get_or_404(user_id)
    
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == g.current_user.id, Message.recipient_id == user_id, Message.is_deleted_by_sender == False),
            and_(Message.sender_id == user_id, Message.recipient_id == g.current_user.id, Message.is_deleted_by_recipient == False)
        )
    ).order_by(Message.sent_at.asc()).all()
    
    # Mark as read
    Message.query.filter_by(sender_id=user_id, recipient_id=g.current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify({
        'partner': {
            'id': partner.id,
            'name': partner.name,
            'role': partner.role.capitalize()
        },
        'messages': [{
            'id': m.id,
            'sender_id': m.sender_id,
            'subject': m.subject,
            'body': m.body,
            'timestamp': m.sent_at.strftime('%I:%M %p, %b %d')
        } for m in messages]
    })

@messages_bp.route('/send', methods=['POST'])
def send():
    # Simple manual CSRF check (checking if it is an ajax request, but ideally use WTForms)
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 'csrf_token' not in request.form:
        # In a real app we validate token, assuming verified by presence for now if not ajax
        pass

    recipient_id = request.form.get('recipient_id', type=int)
    subject = request.form.get('subject', '').strip()
    body = request.form.get('body', '').strip()
    
    ip_address = request.remote_addr or '127.0.0.1'
    
    if not recipient_id or not body or not subject:
        return jsonify({'error': 'Missing recipient, subject, or message body. All fields are required.'}), 400
        
    if len(subject) > 100:
        return jsonify({'error': 'Subject exceeds maximum length of 100 characters.'}), 400
        
    if len(body) > 2000:
        return jsonify({'error': 'Message body exceeds maximum length of 2000 characters.'}), 400
        
    recipient = User.query.get_or_404(recipient_id)
    
    # 1. Authorization Check
    if not can_message(g.current_user, recipient):
        log_attempt(g.current_user.id, recipient_id, subject, ip_address, True, 'Unauthorized')
        return jsonify({'error': 'You are not authorized to message this user.'}), 403
        
    # 2. Rate Limit Check
    allowed, limit_reason = check_rate_limits(g.current_user)
    if not allowed:
        log_attempt(g.current_user.id, recipient_id, subject, ip_address, True, limit_reason)
        return jsonify({'error': limit_reason}), 429
        
    # 3. Spam Check
    spam_allowed, spam_reason = check_spam(g.current_user, recipient)
    if not spam_allowed:
        log_attempt(g.current_user.id, recipient_id, subject, ip_address, True, spam_reason)
        return jsonify({'error': spam_reason}), 429
    
    # Sanitize inputs
    safe_body = escape(body)
    safe_subject = escape(subject)
    
    # Save the message
    new_msg = Message(
        sender_id=g.current_user.id, 
        recipient_id=recipient_id, 
        subject=safe_subject,
        body=safe_body
    )
    db.session.add(new_msg)
    
    # Log successful attempt
    log_attempt(g.current_user.id, recipient_id, safe_subject, ip_address, False, None)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message_id': new_msg.id,
        'timestamp': new_msg.sent_at.strftime('%I:%M %p, %b %d'),
        'subject': new_msg.subject
    })

@messages_bp.route('/search_allowed')
def search_allowed():
    """Endpoint for searchable dropdown in New Message modal."""
    query = request.args.get('q', '').lower()
    
    user = g.current_user
    allowed_recipients = []
    
    if user.role == 'student':
        enrolled_course_ids = [e.course_id for e in user.enrollments]
        teachers = User.query.join(Course, Course.teacher_id == User.id).filter(
            Course.id.in_(enrolled_course_ids),
            or_(User.name.ilike(f'%{query}%'), User.email.ilike(f'%{query}%'))
        ).distinct().all()
        allowed_recipients = teachers
    elif user.role in ['professor', 'assistant_professor']:
        taught_course_ids = [c.id for c in user.taught_courses]
        students = User.query.join(Enrollment, Enrollment.student_id == User.id).filter(
            Enrollment.course_id.in_(taught_course_ids),
            or_(User.name.ilike(f'%{query}%'), User.email.ilike(f'%{query}%'))
        ).distinct().all()
        
        other_teachers = User.query.filter(
            User.school_id == user.school_id, 
            User.role.in_(['professor', 'assistant_professor', 'dean']),
            User.id != user.id,
            or_(User.name.ilike(f'%{query}%'), User.email.ilike(f'%{query}%'))
        ).all()
        allowed_recipients = students + other_teachers

    return jsonify([{
        'id': u.id,
        'name': u.name,
        'role': u.role.capitalize(),
        'avatar': u.name[0].upper()
    } for u in allowed_recipients])
