from flask import Blueprint, render_template, session, request, redirect, url_for, g, jsonify
from app.models import db, User, Message, Friendship, FriendRequest
from sqlalchemy import or_, and_
from datetime import datetime

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

@messages_bp.before_request
def load_user():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    g.current_user = User.query.get(session['user_id'])
    if not g.current_user:
        session.clear()
        return redirect(url_for('auth.login'))

@messages_bp.route('/')
def index():
    user = g.current_user
    # Find all users who have sent/received messages with the current user
    sent_to = db.session.query(Message.recipient_id).filter_by(sender_id=user.id).distinct()
    received_from = db.session.query(Message.sender_id).filter_by(recipient_id=user.id).distinct()
    
    partner_ids = set([r[0] for r in sent_to] + [r[0] for r in received_from])
    partners = User.query.filter(User.id.in_(partner_ids)).all() if partner_ids else []
    
    # Also get friends for the sidebar
    friends = user.friends
    pending_requests = user.pending_requests
    
    return render_template('messages/index.html', 
                           partners=partners, 
                           friends=friends, 
                           pending_requests=pending_requests)

@messages_bp.route('/history/<int:user_id>')
def history(user_id):
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == g.current_user.id, Message.recipient_id == user_id),
            and_(Message.sender_id == user_id, Message.recipient_id == g.current_user.id)
        )
    ).order_by(Message.sent_at.asc()).all()
    
    # Mark as read
    Message.query.filter_by(sender_id=user_id, recipient_id=g.current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify([{
        'id': m.id,
        'sender_id': m.sender_id,
        'body': m.body,
        'timestamp': m.sent_at.strftime('%I:%M %p')
    } for m in messages])

@messages_bp.route('/send', methods=['POST'])
def send():
    recipient_id = request.form.get('recipient_id', type=int)
    body = request.form.get('body')
    
    if not recipient_id or not body:
        return jsonify({'error': 'Missing recipient or body'}), 400
        
    recipient = User.query.get_or_404(recipient_id)
    
    # Check friendship if needed, but for now allow messages
    new_msg = Message(sender_id=g.current_user.id, recipient_id=recipient_id, body=body)
    db.session.add(new_msg)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message_id': new_msg.id,
        'timestamp': new_msg.sent_at.strftime('%I:%M %p')
    })

@messages_bp.route('/block/<int:user_id>', methods=['POST'])
def block(user_id):
    # Minimal block Implementation: just unfriend for now
    friendship = Friendship.query.filter(
        or_(
            and_(Friendship.user1_id == g.current_user.id, Friendship.user2_id == user_id),
            and_(Friendship.user1_id == user_id, Friendship.user2_id == g.current_user.id)
        )
    ).first()
    
    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        
    return redirect(url_for('messages.index'))
