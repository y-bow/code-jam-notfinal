from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from ..models import User, School, bcrypt
import random
import io
import base64
from PIL import Image, ImageDraw, ImageFont

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            if session.get('role') != role and session.get('role') != 'admin':
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_captcha():
    """Generates an alphanumeric image CAPTCHA and stores the answer in the session."""
    # Generate random string
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" # Exclude confusing chars like 0, O, 1, I, l
    captcha_text = "".join(random.choices(chars, k=random.randint(5, 6)))
    session['captcha_answer'] = captcha_text
    
    # Create image
    width, height = 180, 60
    image = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(image)
    
    # Add noise lines
    for _ in range(8):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=(random.randint(150, 200), random.randint(150, 200), random.randint(150, 200)), width=1)

    # Add noise dots
    for _ in range(100):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))

    # Draw text with simple distortion
    try:
        # Try to use a system font if available, otherwise fallback to default
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Draw characters individually with slight rotation simulation (offsetting)
    current_x = 20
    for char in captcha_text:
        char_y = random.randint(10, 25)
        # Using dark colors for text
        draw.text((current_x, char_y), char, fill=(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)), font=font)
        current_x += random.randint(25, 30)

    # Convert to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    session['captcha_image'] = f"data:image/png;base64,{img_str}"
    return session['captcha_image']


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user_captcha = request.form.get('captcha_answer', '').strip()

        # CAPTCHA Validation (Disabled for testing)
        # if user_captcha != session.get('captcha_answer'):
        #     flash('Invalid CAPTCHA. Please try again.', 'danger')
        #     generate_captcha() 
        #     return render_template('login.html')

        # Find user by email (may exist in multiple schools, but email+school is unique)
        # For single-school deployments, this is straightforward.
        # For multi-school, we match by email domain or let the user pick a school.
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return render_template('login.html')

            if user.school and not user.school.is_active:
                flash('Your institution is currently inactive.', 'danger')
                return render_template('login.html')

            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            session['school_id'] = user.school_id
            
            # Special flag for Platform Owner
            if user.role == 'owner':
                session['is_owner'] = True
                return redirect(url_for('owner.dashboard'))

            if user.role in ('student', 'class_rep'):
                return redirect(url_for('dashboard.student_dashboard'))
            elif user.role in ('professor', 'assistant_professor'):
                return redirect(url_for('dashboard.teacher_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('dashboard.admin_dashboard'))
            elif user.role == 'dean':
                return redirect(url_for('dashboard.school_analytics'))
            else:
                return redirect(url_for('index'))

        flash('Invalid email or password', 'danger')
        generate_captcha() # Refresh on failed login

    # Generate CAPTCHA for initial GET request if not already present or on refresh
    generate_captcha()
    return render_template('login.html')


@auth_bp.route('/refresh-captcha', methods=['GET'])
def refresh_captcha():
    """Endpoint to get a new CAPTCHA image via AJAX."""
    image_src = generate_captcha()
    return {"image_src": image_src}


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# Simple in-memory rate limiter for password changes (max 5 attempts / 10 mins)
# In production, use Flask-Limiter or Redis
password_change_attempts = {}

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        import time
        from datetime import datetime
        
        # Rate Limiting Check
        now = time.time()
        attempts = password_change_attempts.get(user.id, [])
        # Filter attempts within the last 10 minutes (600 seconds)
        attempts = [t for t in attempts if now - t < 600]
        if len(attempts) >= 5:
            flash('Too many password change attempts. Please try again in 10 minutes.', 'danger')
            return render_template('change_password.html')
        
        password_change_attempts[user.id] = attempts + [now]

        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not bcrypt.check_password_hash(user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('change_password.html')
            
        if current_password == new_password:
            flash('New password must be different from current password.', 'danger')
            return render_template('change_password.html')
            
        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'danger')
            return render_template('change_password.html')
            
        import re
        if (len(new_password) < 8 or 
            not re.search(r"[A-Z]", new_password) or 
            not re.search(r"[0-9]", new_password) or 
            not re.search(r"[!@#$%^&*]", new_password)):
            flash('New password does not meet the minimum security requirements.', 'danger')
            return render_template('change_password.html')

        # Update Password
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.must_change_password = False
        from ..models import db
        db.session.commit()
        
        # Clear rate limit history on success
        if user.id in password_change_attempts:
            del password_change_attempts[user.id]
            
        flash('Password updated successfully ✓', 'success')

        if user.role in ('student', 'class_rep'):
            return redirect(url_for('dashboard.student_dashboard'))
        elif user.role in ('professor', 'assistant_professor'):
            return redirect(url_for('dashboard.teacher_dashboard'))
        else:
            return redirect(url_for('dashboard.admin_dashboard'))

    return render_template('change_password.html')
