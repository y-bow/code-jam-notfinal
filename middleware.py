"""
Tenant isolation and role-based access control middleware.

Usage in routes:
    @blueprint.route('/courses')
    @school_scoped           # enforces login + loads g.current_user, g.school_id
    @role_minimum('teacher')  # optional: enforces minimum role level
    def list_courses():
        # g.school_id is guaranteed to be set
        # all queries MUST filter by g.school_id
        ...
"""
from functools import wraps
from flask import session, g, abort, flash, redirect, url_for
from models import User, ROLE_HIERARCHY, Message, Announcement


def school_scoped(f):
    """
    Core tenant isolation decorator.

    - Verifies the user is logged in.
    - Loads the full User object into g.current_user.
    - Sets g.school_id from the user's school membership.
    - Ensures the user and their school are active.
    - Populates notification data (unread messages, recent announcements).

    Must be applied BEFORE any role_minimum decorator.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            flash('Account not found or deactivated.', 'danger')
            return redirect(url_for('auth.login'))

        # Verify school is still active
        if not user.school or not user.school.is_active:
            session.clear()
            flash('Your institution is currently inactive.', 'danger')
            return redirect(url_for('auth.login'))

        g.current_user = user
        g.school_id = user.school_id

        # Notification data
        g.unread_messages = Message.query.filter_by(recipient_id=user.id, is_read=False).order_by(Message.sent_at.desc()).limit(5).all()
        g.unread_count = Message.query.filter_by(recipient_id=user.id, is_read=False).count()
        
        # Recent announcements for this school
        g.recent_announcements = Announcement.query.filter_by(school_id=user.school_id).order_by(Announcement.posted_at.desc()).limit(3).all()

        return f(*args, **kwargs)
    return decorated_function


def role_minimum(min_role):
    """
    Enforce a minimum role level. Must be used AFTER @school_scoped.

    Example:
        @school_scoped
        @role_minimum('dean')
        def admin_panel():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user:
                abort(401)

            required_level = ROLE_HIERARCHY.get(min_role)
            if required_level is None:
                raise ValueError(f"Unknown role: {min_role}")

            if user.role_level < required_level:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def owns_resource(resource_obj, school_id_attr='school_id'):
    """
    Validate that a database object belongs to the current user's school.
    Raises 404 if not found, 403 if school mismatch.

    Usage:
        course = Course.query.get_or_404(course_id)
        owns_resource(course.section, 'school_id')
    """
    if resource_obj is None:
        abort(404)

    obj_school_id = getattr(resource_obj, school_id_attr, None)
    if obj_school_id is None:
        abort(404)

    if obj_school_id != g.school_id:
        abort(403)  # Cross-tenant access attempt
