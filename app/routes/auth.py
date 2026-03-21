from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from ..models import User, School, Student, Section, bcrypt, db
from .. import limiter
import random
import io
import base64
import re
import secrets
from datetime import datetime, timedelta
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
@limiter.limit("5 per 15 minutes")
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return render_template('login.html')

            if user.is_suspended:
                flash('Your account is currently suspended. Contact support.', 'danger')
                return render_template('login.html')

            # Skip school checks for platform owner
            if user.role != 'platform_owner':
                if user.school and not user.school.is_active:
                    flash('Your university account is currently suspended. Contact your administrator.', 'danger')
                    return render_template('login.html')

            # Store in session as per security requirements
            session.permanent = True
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            session['school_id'] = user.school_id
            session['school_name'] = user.school.name if user.school else 'Hive Platform'
            session['is_platform_owner'] = (user.role == 'platform_owner')

            if user.role in ('student', 'class_rep'):
                return redirect(url_for('dashboard.student_dashboard'))
            elif user.role in ('professor', 'assistant_professor'):
                return redirect(url_for('dashboard.teacher_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('dashboard.admin_dashboard'))
            elif user.role == 'dean':
                return redirect(url_for('dashboard.school_analytics'))
            elif user.role == 'platform_owner':
                return redirect(url_for('dashboard.admin_dashboard')) # Or a specific owner dashboard
            else:
                return redirect(url_for('index'))

        flash('Invalid email or password', 'danger')
        generate_captcha()

    generate_captcha()
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Password validation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[0-9]", password) or not re.search(r"[!@#$%^&*]", password):
            flash('Password must be at least 8 chars, with uppercase, number, and special char.', 'danger')
            return render_template('register.html')

        # Single University Enforcement
        email_domain = email.split('@')[-1] if '@' in email else ''
        school = School.query.filter_by(domain=email_domain).first()

        if not school:
            flash('Your email domain is not registered on Hive. Ask your university administrator to register your institution.', 'danger')
            return render_template('register.html')

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.school_id:
                flash(f'You are already enrolled at {existing_user.school.name}. Hive does not support multiple university enrollment. Contact support if this is an error.', 'danger')
            else:
                flash('An account with this email already exists.', 'danger')
            return render_template('register.html')

        # Create User
        new_user = User(
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            role='student',
            name=name,
            school_id=school.id,
            is_active=True
        )
        db.session.add(new_user)
        db.session.flush() # Get user ID

        # Create Student Profile (Section assignment logic might be needed, but for now we pick first)
        section = Section.query.filter_by(school_id=school.id).first()
        if not section:
            flash('University has no sections configured. Contact administrator.', 'danger')
            db.session.rollback()
            return render_template('register.html')

        student_profile = Student(
            user_id=new_user.id,
            school_id=school.id,
            section_id=section.id,
            enrollment_year=datetime.utcnow().year
        )
        db.session.add(student_profile)
        db.session.commit()

        flash('Successfully registered! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


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


# Password Reset Logic
reset_tokens = {} # In-memory store: {token: (email, expires_at)}

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def request_reset():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = secrets.token_urlsafe(32)
            reset_tokens[token] = (email, datetime.utcnow() + timedelta(hours=1))
            # In a real app, send email here. For now, log to console.
            print(f"PASSWORD RESET LINK: {url_for('auth.reset_with_token', token=token, _external=True)}")
            flash('If an account matches that email, a reset link has been sent.', 'info')
        else:
            # Same message to prevent email enumeration
            flash('If an account matches that email, a reset link has been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('request_reset.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    token_data = reset_tokens.get(token)
    if not token_data:
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('auth.login'))
    
    email, expires_at = token_data
    if datetime.utcnow() > expires_at:
        reset_tokens.pop(token, None)
        flash('Reset token has expired.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)
        
        if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[0-9]", password) or not re.search(r"[!@#$%^&*]", password):
            flash('Password insecure.', 'danger')
            return render_template('reset_password.html', token=token)
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.commit()
            reset_tokens.pop(token, None)
            
            # Invalidate all existing sessions for this user
            # In Flask session (cookie-based), we can't easily invalidate other sessions 
            # without a server-side session store. But we can change a 'session_version' or use Flask-Login.
            # For this requirement, we'll clear the current session.
            session.clear()
            
            flash('Password reset successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
    return render_template('reset_password.html', token=token)
