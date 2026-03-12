from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g, jsonify
from app.models import db, User, FriendRequest, Friendship
from sqlalchemy import or_

social_bp = Blueprint('social', __name__, url_prefix='/social')

@social_bp.before_request
def load_user():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    g.current_user = User.query.get(session['user_id'])
    if not g.current_user:
        session.clear()
        return redirect(url_for('auth.login'))

@social_bp.route('/friends')
def friends():
    search_query = request.args.get('q', '')
    search_results = []
    
    if search_query:
        # Search for users by name or email (excluding self)
        search_results = User.query.filter(
            User.id != g.current_user.id,
            User.school_id == g.current_user.school_id, # Stay within school for now
            or_(
                User.name.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%')
            )
        ).limit(10).all()

    return render_template('social/friends.html', 
                           friends=g.current_user.friends,
                           pending_requests=g.current_user.pending_requests,
                           search_results=search_results,
                           search_query=search_query)

@social_bp.route('/request/<int:user_id>', methods=['POST'])
def send_request(user_id):
    if user_id == g.current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'You cannot add yourself.'}), 400
        flash('You cannot add yourself as a friend.', 'warning')
        return redirect(url_for('social.friends'))
    
    recipient = User.query.get_or_404(user_id)
    
    # Check if already friends
    if g.current_user.is_friends_with(user_id):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Already friends.'}), 400
        flash(f'You are already friends with {recipient.name}.', 'info')
        return redirect(url_for('social.friends'))
    
    # Check if a request already exists
    existing = FriendRequest.query.filter(
        ((FriendRequest.sender_id == g.current_user.id) & (FriendRequest.recipient_id == user_id)) |
        ((FriendRequest.sender_id == user_id) & (FriendRequest.recipient_id == g.current_user.id))
    ).first() # Check ANY status (pending/accepted) to be safe
    
    if existing:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Request already exists.'}), 400
        flash('A friend request already exists.', 'info')
        return redirect(url_for('social.friends'))
    
    new_request = FriendRequest(sender_id=g.current_user.id, recipient_id=user_id)
    db.session.add(new_request)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Request sent.'})
        
    flash(f'Friend request sent to {recipient.name}.', 'success')
    return redirect(url_for('social.friends'))

@social_bp.route('/accept/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    req = FriendRequest.query.get_or_404(request_id)
    
    if req.recipient_id != g.current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Unauthorized'}), 403
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('social.friends'))
    
    # Create friendship
    friendship = Friendship(user1_id=req.sender_id, user2_id=req.recipient_id)
    db.session.add(friendship)
    
    # Delete request
    db.session.delete(req)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Accepted.'})
        
    flash('Friend request accepted.', 'success')
    return redirect(url_for('messages.index')) # Redirect to messages to be safe

@social_bp.route('/decline/<int:request_id>', methods=['POST'])
def decline_request(request_id):
    req = FriendRequest.query.get_or_404(request_id)
    
    if req.recipient_id != g.current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Unauthorized'}), 403
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('social.friends'))
    
    db.session.delete(req)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Declined.'})
        
    flash('Friend request declined.', 'info')
    return redirect(url_for('messages.index'))

@social_bp.route('/unfriend/<int:user_id>', methods=['POST'])
def unfriend(user_id):
    friendship = Friendship.query.filter(
        ((Friendship.user1_id == g.current_user.id) & (Friendship.user2_id == user_id)) |
        ((Friendship.user1_id == user_id) & (Friendship.user2_id == g.current_user.id))
    ).first()
    
    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Unfriended.'})
        flash('Friend removed.', 'info')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Friendship not found.'}), 404
        flash('Friendship not found.', 'warning')
        
    return redirect(url_for('messages.index'))

@social_bp.route('/search_ajax')
def search_ajax():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = User.query.filter(
        User.id != g.current_user.id,
        User.school_id == g.current_user.school_id,
        or_(
            User.name.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%')
        )
    ).limit(5).all()
    
    return jsonify([{
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'avatar': u.name[0].upper(),
        'is_friend': g.current_user.is_friends_with(u.id),
        'sent_request': g.current_user.has_pending_request_to(u.id),
        'received_request': g.current_user.has_pending_request_from(u.id)
    } for u in results])
