from app import create_app
from app.models import (
    db, User, Student, Teacher, School, Section,
    Course, Enrollment, Announcement, TimetableEntry, bcrypt,
    TeacherTodo, TeacherRating, Message, Internship, LostFoundItem,
    Club, ExternalEvent, ProfessorAssistantAssignment, ClassRepNomination,
    UploadedFile, UploadLog, UniversityRegistration, InviteToken, JoinCode
)
from datetime import datetime, timedelta

app = create_app()

def seed_db():
    with app.app_context():
        # Drop and recreate all tables
        db.metadata.drop_all(bind=db.engine)
        db.create_all()
        print("Tables created.")

        pw = bcrypt.generate_password_hash('password123').decode('utf-8')

        # =====================================================================
        # 1. PLATFORM OWNER
        # =====================================================================
        owner = User(
            email='owner@hive.app',
            password_hash=pw,
            role='platform_owner',
            name='Hive Owner',
            school_id=None,
            must_change_password=True
        )
        db.session.add(owner)
        db.session.commit()

        # =====================================================================
        # 2. UNIVERSITIES
        # =====================================================================
        
        # --- University A: Apex Institute of Technology ---
        apex = School(
            name='Apex Institute of Technology',
            slug='apex-institute',
            domain='apex.edu.in',
            ugc_number='UGC-DEMO-001',
            trust_level='verified',
            country='India',
            is_active=True,
            approved_at=datetime.utcnow(),
            approved_by=owner.id
        )
        db.session.add(apex)
        
        # --- University B: Greenfield University ---
        greenfield = School(
            name='Greenfield University',
            slug='greenfield-university',
            domain='greenfield.ac.in',
            ugc_number='UGC-DEMO-002',
            trust_level='verified',
            country='India',
            is_active=True,
            approved_at=datetime.utcnow(),
            approved_by=owner.id
        )
        db.session.add(greenfield)
        db.session.commit()

        def seed_university(school):
            # Admin
            admin = User(school_id=school.id, email=f'admin@{school.domain}',
                         password_hash=pw, role='admin', name=f'{school.name} Admin')
            
            # Dean
            dean = User(school_id=school.id, email=f'dean@{school.domain}',
                        password_hash=pw, role='dean', name=f'Dr. {school.slug.split("-")[0].capitalize()} Dean')
            
            db.session.add_all([admin, dean])
            db.session.commit()

            # 5 Professors
            profs = []
            for i in range(1, 6):
                prof = User(school_id=school.id, email=f'prof{i}@{school.domain}',
                            password_hash=pw, role='professor', name=f'Professor {i}')
                profs.append(prof)
            
            # 1 Assistant Professor
            asst_prof = User(school_id=school.id, email=f'asst@{school.domain}',
                             password_hash=pw, role='assistant_professor', name='Assistant Professor')
            
            db.session.add_all(profs + [asst_prof])
            db.session.commit()

            # Sections
            sec1 = Section(school_id=school.id, name='Section A', code='SEC-A', batch_year=2025)
            db.session.add(sec1)
            db.session.commit()

            # Students
            for i in range(1, 11):
                student_user = User(school_id=school.id, email=f'student{i}@{school.domain}',
                                    password_hash=pw, role='student', name=f'Student {i}')
                db.session.add(student_user)
                db.session.commit()
                
                student_profile = Student(
                    user_id=student_user.id,
                    school_id=school.id,
                    section_id=sec1.id,
                    enrollment_year=2025,
                    student_id_number=f'ROLL-{school.slug[:3].upper()}-{i:03d}'
                )
                db.session.add(student_profile)
            
            db.session.commit()

            # Course
            course = Course(section_id=sec1.id, name='Introduction to Engineering', code='ENG101', 
                            teacher_id=profs[0].id, credits=4)
            db.session.add(course)
            db.session.commit()

        seed_university(apex)
        seed_university(greenfield)

        print("Database seeded successfully with multi-tenancy!")

if __name__ == '__main__':
    seed_db()

"""
MIGRATION SQL (PostgreSQL/SQLite compatible)
---

-- 1. Create Schools Table
CREATE TABLE schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(100) DEFAULT 'India',
    ugc_number VARCHAR(50),
    trust_level VARCHAR(20) DEFAULT 'pending',
    logo_url VARCHAR(500),
    accent_color VARCHAR(7) DEFAULT '#3B82F6',
    website_url VARCHAR(200),
    address TEXT,
    established_year INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    approved_by INTEGER,
    FOREIGN KEY(approved_by) REFERENCES users(id)
);

-- 2. Update Users Table
ALTER TABLE users ADD COLUMN one_school_enforced BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN is_suspended BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN suspension_reason VARCHAR(500);
ALTER TABLE users ADD COLUMN last_login_at DATETIME;

-- 3. Update Students Table
ALTER TABLE students ADD COLUMN school_id INTEGER NOT NULL;
ALTER TABLE students ADD COLUMN student_id_number VARCHAR(50);
ALTER TABLE students ADD COLUMN joined_at DATETIME DEFAULT CURRENT_TIMESTAMP;
CREATE UNIQUE INDEX uq_student_user_school ON students(user_id, school_id);

-- 4. Create UploadedFile Table
CREATE TABLE uploaded_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    uploaded_by INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    processing_errors TEXT,
    FOREIGN KEY(school_id) REFERENCES schools(id),
    FOREIGN KEY(uploaded_by) REFERENCES users(id)
);

-- 5. Create UploadLog Table
CREATE TABLE upload_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    message TEXT,
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(upload_id) REFERENCES uploaded_files(id)
);

-- 6. Create UniversityRegistration Table
CREATE TABLE university_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_name VARCHAR(200) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    ugc_number VARCHAR(50) NOT NULL,
    rep_name VARCHAR(100) NOT NULL,
    rep_email VARCHAR(120) NOT NULL,
    rep_designation VARCHAR(100) NOT NULL,
    website_url VARCHAR(200),
    country VARCHAR(100) DEFAULT 'India',
    status VARCHAR(20) DEFAULT 'pending',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    decided_at DATETIME,
    decision_by INTEGER,
    rejection_reason TEXT,
    FOREIGN KEY(decision_by) REFERENCES users(id)
);

-- 7. Create InviteToken Table
CREATE TABLE invite_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token VARCHAR(32) UNIQUE NOT NULL,
    school_id INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_by INTEGER NOT NULL,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    used_by INTEGER,
    used_at DATETIME,
    FOREIGN KEY(school_id) REFERENCES schools(id),
    FOREIGN KEY(created_by) REFERENCES users(id),
    FOREIGN KEY(used_by) REFERENCES users(id)
);

-- 8. Create JoinCode Table
CREATE TABLE join_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(6) UNIQUE NOT NULL,
    course_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    max_uses INTEGER,
    use_count INTEGER DEFAULT 0,
    FOREIGN KEY(course_id) REFERENCES courses(id),
    FOREIGN KEY(section_id) REFERENCES sections(id),
    FOREIGN KEY(created_by) REFERENCES users(id)
);

-- 9. Create ProfessorAssistantAssignment Table
CREATE TABLE professor_assistant_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    professor_id INTEGER NOT NULL,
    assistant_id INTEGER NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at DATETIME,
    FOREIGN KEY(course_id) REFERENCES courses(id),
    FOREIGN KEY(professor_id) REFERENCES users(id),
    FOREIGN KEY(assistant_id) REFERENCES users(id)
);

-- 10. Update ClassRepNomination Table
ALTER TABLE class_rep_nominations ADD COLUMN rejection_reason TEXT;
"""
