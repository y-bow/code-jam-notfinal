import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, abort

from ..models import db, LostFoundItem, Message
from ..permissions import (
    require_role, require_min_role, student_required, 
    dean_required, admin_required, school_scope
)

lost_found_bp = Blueprint('lost_found', __name__, url_prefix='/lost-found')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@lost_found_bp.route('/gallery', methods=['GET'])
@student_required
def gallery():
    query_str = request.args.get('q', '')
    category = request.args.get('category', '')
    report_type = request.args.get('type', '')

    # Use school_scope for automatic multi-tenancy
    base_query = school_scope(LostFoundItem.query, LostFoundItem).filter_by(status='open')
    
    if query_str:
        base_query = base_query.filter(
            (LostFoundItem.title.ilike(f'%{query_str}%')) | 
            (LostFoundItem.location.ilike(f'%{query_str}%'))
        )
    if category:
        base_query = base_query.filter_by(category=category)
    if report_type:
        base_query = base_query.filter_by(report_type=report_type)

    items = base_query.order_by(LostFoundItem.timestamp.desc()).all()
    categories = ['Electronics', 'ID Cards', 'Books', 'Clothing', 'Accessories', 'Other']

    return render_template('lost_found/gallery.html', 
                            items=items, 
                            query=query_str, 
                            selected_category=category,
                            selected_type=report_type,
                            categories=categories)

@lost_found_bp.route('/my-items', methods=['GET'])
@student_required
def my_items():
    items = school_scope(LostFoundItem.query, LostFoundItem).filter_by(
        reporter_id=g.current_user.id
    ).order_by(LostFoundItem.timestamp.desc()).all()
    
    return render_template('lost_found/my_items.html', items=items)

@lost_found_bp.route('/report', methods=['GET', 'POST'])
@student_required
def report():
    categories = ['Electronics', 'ID Cards', 'Books', 'Clothing', 'Accessories', 'Other']
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        category = request.form.get('category')
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        
        if not all([report_type, category, title, description, location]):
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for('lost_found.report'))

        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"user_{g.current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
                upload_folder = os.path.join(current_app.static_folder, 'uploads', 'lost_found')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                image_path = f"uploads/lost_found/{filename}"

        new_item = LostFoundItem(
            school_id=g.school_id,
            reporter_id=g.current_user.id,
            report_type=report_type,
            category=category,
            title=title,
            description=description,
            location=location,
            image_path=image_path
        )
        db.session.add(new_item)
        db.session.flush() # get new_item.id

        # Matching Logic
        if report_type == 'found':
            # look for open 'lost' items of same category in the SAME school
            potential_matches = school_scope(LostFoundItem.query, LostFoundItem).filter_by(
                report_type='lost',
                status='open',
                category=category
            ).all()

            matched = False
            for lost_item in potential_matches:
                # Basic matching (title or description overlap)
                words_found = set(title.lower().split() + description.lower().split())
                words_lost = set(lost_item.title.lower().split() + lost_item.description.lower().split())
                
                overlap = words_found.intersection(words_lost)
                if len(overlap) >= 2: # heuristic: at least 2 common words
                    # Notification!
                    msg_body = f"A found item '{title}' might match your lost item '{lost_item.title}'. Check the Lost & Found gallery!"
                    notif = Message(
                        sender_id=g.current_user.id,
                        recipient_id=lost_item.reporter_id,
                        subject="Lost & Found Match",
                        body=msg_body
                    )
                    db.session.add(notif)
                    matched = True
            
            if matched:
                flash("Item reported successfully! We notified users whose lost items might match yours.", "success")
            else:
                flash("Item reported successfully!", "success")
        else:
            flash("Lost item reported successfully!", "success")

        db.session.commit()
        return redirect(url_for('lost_found.gallery'))

    return render_template('lost_found/report.html', categories=categories)

@lost_found_bp.route('/resolve/<int:item_id>', methods=['POST'])
@student_required
def resolve(item_id):
    # Use school_scope to ensure admin/platform_owner can see it globally or per school
    item = school_scope(LostFoundItem.query, LostFoundItem).filter_by(id=item_id).first_or_404()
    
    # Permission check: Admin/Platform Owner can resolve anything they see, 
    # others can only resolve their own reports.
    can_resolve = False
    if g.current_user.role in ('admin', 'platform_owner', 'dean'):
        can_resolve = True
    elif item.reporter_id == g.current_user.id:
        can_resolve = True
        
    if not can_resolve:
        abort(403)
    
    item.status = 'resolved'
    db.session.commit()
    flash(f"Item '{item.title}' marked as resolved.", "success")
    return redirect(url_for('lost_found.my_items'))

