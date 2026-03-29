import os
from app import create_app
from app.models import db, School, Section, User, Student, Teacher, bcrypt
from datetime import datetime

# Initialize the Flask application
app = create_app()

def clear_data():
    """Drops and recreates all tables for a clean start."""
    print("Clearing existing data...")
    db.drop_all()
    db.create_all()
    print("Database structure reset.")

def seed_schools():
    """Seeds the 8 schools requested."""
    schools_data = [
        ("School of Arts and Sciences", "SAS", "sas.apex.edu.in"),
        ("School of Computing and Data Science", "SCDS", "scds.saiuniversity.edu.in"),
        ("School of Law", "SOL", "sol.apex.edu.in"),
        ("School of Artificial Intelligence", "SOAI", "soai.apex.edu.in"),
        ("School of Media", "SOM", "som.apex.edu.in"),
        ("School of Technology", "SOT", "sot.apex.edu.in"),
        ("School of Business", "SOB", "sob.apex.edu.in"),
        ("School of Allied Health Sciences", "SAHS", "sahs.apex.edu.in"),
    ]
    
    schools = {}
    for name, code, domain in schools_data:
        # Idempotency check
        existing = School.query.filter_by(code=code).first()
        if existing:
            print(f"⏩ School {code} already exists.")
            schools[code] = existing
            continue
            
        school = School(name=name, code=code, domain=domain)
        db.session.add(school)
        db.session.flush()
        schools[code] = school
        print(f"Added school: {name}")
    
    db.session.commit()
    return schools

def seed_sections(scds_school):
    """Seeds 7 sections for Computer Science under SCDS."""
    sections = []
    for i in range(1, 8):
        code = f"SCDS-CS-S{i}"
        existing = Section.query.filter_by(code=code, school_id=scds_school.id).first()
        if existing:
            print(f"⏩ Section {code} already exists.")
            sections.append(existing)
            continue
            
        section = Section(
            school_id=scds_school.id,
            name=f"Section {i}",
            code=code,
            batch_year=2025
        )
        db.session.add(section)
        sections.append(section)
        print(f"Added section: {section.name}")
    
    db.session.commit()
    return sections

def seed_users(scds_school, sections):
    """Seeds specific students and placeholder users."""
    pw_hash = bcrypt.generate_password_hash("hive@1234").decode('utf-8')
    
    # Selection of section 3 for seeding targets
    section_3 = sections[2] # Index 2 is Section 3

    # 1. Specific Students
    students_to_seed = [
        {
            "name": "B. Vaibhav",
            "email": "vaibhav.b-29@scds.saiuniversity.edu.in",
            "app_id": "CDS/2025/1179"
        },
        {
            "name": "Riddhima P.",
            "email": "ruddhima.p-29@scds.saiuniversity.edu.in",
            "app_id": None
        },
        {
            "name": "Harshitha B.",
            "email": "harshitha.b-29@scds.saiuniversity.edu.in",
            "app_id": None
        }
    ]

    for s_data in students_to_seed:
        existing = User.query.filter_by(email=s_data['email']).first()
        if existing:
            print(f"⏩ User {s_data['email']} already exists.")
            continue
            
        user = User(
            school_id=scds_school.id,
            email=s_data['email'],
            password_hash=pw_hash,
            role='student',
            name=s_data['name']
        )
        db.session.add(user)
        db.session.flush()
        
        student_profile = Student(
            user_id=user.id,
            section_id=section_3.id,
            enrollment_year=2025,
            major="Computer Science"
        )
        db.session.add(student_profile)
        print(f"Added student: {user.name}")

    # 2. Placeholder Users
    placeholders = [
        ("Superadmin", "superadmin@saiuniversity.edu.in", "superadmin", None, None),
        ("Admin", "admin@saiuniversity.edu.in", "admin", None, None),
        ("Dean", "dean@scds.saiuniversity.edu.in", "dean", scds_school.id, None),
        ("Professor", "professor@scds.saiuniversity.edu.in", "professor", scds_school.id, None),
        ("Assistant Professor", "assistant@scds.saiuniversity.edu.in", "assistant_professor", scds_school.id, None),
        ("Class Representative", "rep@scds.saiuniversity.edu.in", "class_rep", scds_school.id, section_3.id)
    ]

    for name, email, role, school_id, sec_id in placeholders:
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"⏩ Placeholder {role} already exists.")
            continue
            
        user = User(
            school_id=school_id,
            email=email,
            password_hash=pw_hash,
            role=role,
            name=name
        )
        db.session.add(user)
        db.session.flush()
        
        if role == 'class_rep':
            student_profile = Student(
                user_id=user.id,
                section_id=sec_id,
                enrollment_year=2025,
                major="Computer Science"
            )
            db.session.add(student_profile)
        elif role in ('professor', 'assistant_professor'):
            teacher_profile = Teacher(
                user_id=user.id,
                department="Computer Science"
            )
            db.session.add(teacher_profile)
        # Dean and Admin/Superadmin don't strictly need extra profiles in this schema
        
        print(f"Added placeholder: {name} ({role})")

    db.session.commit()

def run_seed():
    with app.app_context():
        # Clear database as requested for "RESET"
        clear_data()
        
        # Seed
        schools = seed_schools()
        scds = schools['SCDS']
        sections = seed_sections(scds)
        seed_users(scds, sections)
        
        print("\nDatabase seeded successfully!")

if __name__ == "__main__":
    run_seed()
