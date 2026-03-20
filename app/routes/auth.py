from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from ..models import User, School, UniversityRegistration, InviteToken, Section, Student, bcrypt, db
import secrets
from datetime import datetime, timedelta

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


# =============================================================================
# UNIVERSITY REGISTRATION FLOW
# =============================================================================

@auth_bp.route('/register/university', methods=['GET', 'POST'])
def register_university():
    if request.method == 'POST':
        name = request.form.get('name')
        website_url = request.form.get('website_url')
        country = request.form.get('country', 'India')
        recognition_number = request.form.get('recognition_number')
        rep_name = request.form.get('rep_name')
        rep_email = request.form.get('rep_email', '').strip().lower()
        rep_designation = request.form.get('rep_designation')
        domain = request.form.get('domain', '').strip().lower()

        # Validation
        if not all([name, website_url, rep_name, rep_email, rep_designation, domain]):
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/register_university.html')

        # Validate rep email matches declared domain
        if not rep_email.endswith('@' + domain) and not rep_email.endswith('.' + domain):
            flash(f'Representative email must match the university domain (@{domain}).', 'danger')
            return render_template('auth/register_university.html')

        # Validate domain is not already registered
        existing_school = School.query.filter_by(domain=domain).first()
        if existing_school:
            flash('This university domain is already registered on Hive.', 'danger')
            return render_template('auth/register_university.html')

        existing_reg = UniversityRegistration.query.filter_by(domain=domain).first()
        if existing_reg:
            flash('An application for this domain is already pending.', 'warning')
            return render_template('auth/register_university.html')

        # Create Registration record
        token = secrets.token_urlsafe(32)
        new_reg = UniversityRegistration(
            name=name,
            website_url=website_url,
            country=country,
            recognition_number=recognition_number,
            rep_name=rep_name,
            rep_email=rep_email,
            rep_designation=rep_designation,
            domain=domain,
            verification_token=token,
            status='pending'
        )
        db.session.add(new_reg)
        db.session.commit()

        # Mock Email Verification
        print(f"\n--- [DEMO] Verification Email ---")
        print(f"To: {rep_email}")
        print(f"Subject: Verify your University Application - Hive LMS")
        print(f"Body: Click here to verify: {url_for('auth.verify_university', token=token, _external=True)}")
        print(f"----------------------------------\n")

        # Notify Platform Owner (Mock)
        print(f"\n--- [DEMO] Platform Owner Notification ---")
        print(f"To: owner@hive.app")
        print(f"Subject: New University Application: {name}")
        print(f"Body: A new application from {rep_name} ({rep_email}) is pending review.")
        print(f"------------------------------------------\n")

        return render_template('auth/register_confirmation.html', 
                               message="Application submitted. Please verify your email. You will receive approval within 24-48 hours.")

    return render_template('auth/register_university.html')


@auth_bp.route('/register/verify/<token>')
def verify_university(token):
    reg = UniversityRegistration.query.filter_by(verification_token=token).first()
    if not reg:
        flash('Invalid or expired verification token.', 'danger')
        return redirect(url_for('auth.login'))

    if reg.status == 'pending':
        reg.status = 'verified'
        db.session.commit()
        flash('Email verified! Your application is now being reviewed by the platform owner.', 'success')
    elif reg.status == 'verified':
        flash('Email already verified.', 'info')
    
    return render_template('auth/register_confirmation.html', 
                           message="Email verified. Your application is under review.")


@auth_bp.route('/register/approve/<int:reg_id>')
def approve_university(reg_id):
    # In a real app, this would be protected by platform_owner_required
    reg = UniversityRegistration.query.get_or_404(reg_id)
    
    if reg.status != 'verified' and reg.status != 'pending':
        flash('Registration is already processed or not verified.', 'warning')
        return redirect(url_for('auth.login'))

    # 1. Create School
    school_code = reg.name[:4].upper() + str(random.randint(10, 99))
    new_school = School(
        name=reg.name,
        code=school_code,
        domain=reg.domain,
        is_active=True,
        onboarding_completed=False
    )
    db.session.add(new_school)
    db.session.flush() # Get ID

    # 2. Create Admin Account
    admin_email = f"admin@{reg.domain}"
    temp_password = secrets.token_urlsafe(8)
    admin_user = User(
        school_id=new_school.id,
        email=admin_email,
        password_hash=bcrypt.generate_password_hash(temp_password).decode('utf-8'),
        role='admin',
        name=f"Admin @ {reg.name}",
        must_change_password=True
    )
    db.session.add(admin_user)

    # 3. Update registration status
    reg.status = 'approved'
    db.session.commit()

    # 4. Mock Welcome Email
    welcome_msg = (
        f"\n--- [DEMO] Welcome Email to University Admin ---\n"
        f"To: {admin_email}\n"
        f"Subject: Welcome to Hive LMS - Your University is Ready\n"
        f"Body: Your university instance is ready.\n"
        f"Login at: {url_for('auth.login', _external=True)}\n"
        f"Credentials:\n"
        f"Email: {admin_email}\n"
        f"Password: {temp_password}\n"
        f"(You will be required to change your password on first login)\n\n"
        f"Onboarding Checklist: {url_for('dashboard.admin_dashboard', _external=True)}\n"
        f"--------------------------------------------------\n"
    )
    print(welcome_msg)

    flash(f'University {reg.name} approved! Admin account created: {admin_email}', 'success')
    return redirect(url_for('auth.login'))


# =============================================================================
# STUDENT SELF-REGISTRATION
# =============================================================================

@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        if not all([name, email, password]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register_student.html')

        # Extract domain
        if '@' not in email:
            flash('Invalid email address.', 'danger')
            return render_template('auth/register_student.html')
        
        domain = email.split('@')[-1]

        # Match domain against School
        school = School.query.filter_by(domain=domain).first()
        if not school:
            flash('No university found for this email domain. Contact your university administrator.', 'danger')
            return render_template('auth/register_student.html')

        # Check if student already exists
        existing_user = User.query.filter_by(email=email, school_id=school.id).first()
        if existing_user:
            flash(f'You are already enrolled at {school.name}. A student can only belong to one university.', 'danger')
            return render_template('auth/register_student.html')

        # Create User
        new_user = User(
            school_id=school.id,
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            role='student',
            name=name,
            is_active=False # Pending email verification
        )
        db.session.add(new_user)
        db.session.commit()

        # Mock Verification Email
        print(f"\n--- [DEMO] Student Verification Email ---")
        print(f"To: {email}")
        print(f"Subject: Verify your Student Account - Hive LMS")
        print(f"Body: Your account at {school.name} is ready. Please verify your email to log in.")
        print(f"------------------------------------------\n")

        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_student.html')


# =============================================================================
# STAFF REGISTRATION VIA INVITE
# =============================================================================

@auth_bp.route('/register/invite/<token>', methods=['GET', 'POST'])
def register_invite(token):
    invite = InviteToken.query.filter_by(token=token).first()
    
    if not invite or not invite.is_valid():
        flash('Invalid, expired, or already used invite link.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        if not all([name, password]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register_invite.html', invite=invite)

        # Create User
        new_user = User(
            school_id=invite.school_id,
            email=invite.email,
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            role=invite.role,
            name=name,
            is_active=True
        )
        db.session.add(new_user)
        
        # Mark token as used
        invite.used_at = datetime.utcnow()
        db.session.commit()

        flash(f'Account created for {invite.role.replace("_", " ").title()}! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_invite.html', invite=invite)

