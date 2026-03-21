from functools import wraps
from flask import session, abort, redirect, url_for, flash

ROLE_HIERARCHY = {
    'student': 1,
    'class_rep': 2,
    'assistant_professor': 3,
    'professor': 4,
    'dean': 5,
    'admin': 10,
    'platform_owner': 99
}

def get_current_user():
    from app.models import User
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                return redirect(url_for('auth.login'))
            if user.is_suspended:
                abort(403)
            if user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator

def require_min_role(min_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                return redirect(url_for('auth.login'))
            if user.is_suspended:
                abort(403)
            if ROLE_HIERARCHY.get(user.role, 0) < ROLE_HIERARCHY.get(min_role, 0):
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator

def school_scope(query, model):
    user = get_current_user()
    if not user:
        return query.filter(False) # Should not happen if decorated
    if user.role in ('admin', 'platform_owner'):
        return query
    # For all other roles, restrict to their school
    return query.filter_by(school_id=user.school_id)

# Shortcut decorators
def student_required(f):
    return require_min_role('student')(f)

def professor_required(f):
    return require_min_role('professor')(f)

def dean_required(f):
    return require_min_role('dean')(f)

def admin_required(f):
    return require_role('admin')(f)

def platform_owner_required(f):
    return require_role('platform_owner')(f)
