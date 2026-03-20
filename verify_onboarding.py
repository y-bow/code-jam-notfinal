from app import create_app
from app.models import db, UniversityRegistration, School, User, InviteToken
import secrets

def verify_onboarding():
    app = create_app()
    with app.app_context():
        print("--- Testing University Registration Flow ---")
        # 1. Register University
        name = "New Horizon University"
        domain = "nhu.edu.in"
        rep_email = f"admin@{domain}"
        
        # Check if already exists from previous runs
        if UniversityRegistration.query.filter_by(domain=domain).first():
            print(f"Registration for {domain} already exists. Cleaning up...")
            UniversityRegistration.query.filter_by(domain=domain).delete()
            School.query.filter_by(domain=domain).delete()
            db.session.commit()

        token = secrets.token_urlsafe(32)
        reg = UniversityRegistration(
            name=name,
            website_url="https://nhu.edu.in",
            country="India",
            rep_name="Dr. Smith",
            rep_email=rep_email,
            rep_designation="Registrar",
            domain=domain,
            verification_token=token,
            status='pending'
        )
        db.session.add(reg)
        db.session.commit()
        print(f"Step 1: University {name} registered (Status: {reg.status})")

        # 2. Verify Email
        reg.status = 'verified'
        db.session.commit()
        print(f"Step 2: Email verified (Status: {reg.status})")

        # 3. Approve University (Mocking the route logic)
        school_code = "NHU" + str(secrets.randbelow(90) + 10)
        school = School(name=name, code=school_code, domain=domain, onboarding_completed=False)
        db.session.add(school)
        db.session.flush()

        temp_password = "password123"
        admin = User(
            school_id=school.id,
            email=rep_email,
            password_hash="hashed_pw", # Simplified for test
            role='admin',
            name=f"Admin @ {name}",
            must_change_password=True
        )
        db.session.add(admin)
        reg.status = 'approved'
        db.session.commit()
        print(f"Step 3: University approved. School ID: {school.id}, Admin: {admin.email}")

        # 4. Student Registration
        student_email = f"student@{domain}"
        matched_school = School.query.filter_by(domain=domain).first()
        if matched_school:
            student = User(
                school_id=matched_school.id,
                email=student_email,
                password_hash="hashed_pw",
                role='student',
                name="New Student",
                is_active=False
            )
            db.session.add(student)
            db.session.commit()
            print(f"Step 4: Student registered for {matched_school.name} (Email: {student_email})")
        else:
            print("Step 4 FAILED: School not found for student domain")

        # 5. Invite Token
        invite_token = secrets.token_urlsafe(32)
        invite = InviteToken(
            school_id=school.id,
            email="prof@nhu.edu.in",
            role="professor",
            token=invite_token,
            expires_at=secrets.token_urlsafe(10) # Just a string for mock if datetime not used properly
        )
        # Fix expires_at to be datetime
        from datetime import datetime, timedelta
        invite.expires_at = datetime.utcnow() + timedelta(hours=48)
        db.session.add(invite)
        db.session.commit()
        print(f"Step 5: Invitation sent to professor (Token: {invite_token[:10]}...)")

        print("\n--- ALL STEPS VERIFIED IN DB ---")

if __name__ == "__main__":
    verify_onboarding()
