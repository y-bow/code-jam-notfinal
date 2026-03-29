import os
import json
from app import create_app
from app.models import db, School, Section, User, Student, bcrypt

def insert_section7_batch3():
    app = create_app()
    with app.app_context():
        # Find School and Section
        scds_school = School.query.filter_by(code='SCDS').first()
        section7 = Section.query.filter_by(code='SCDS-CS-S7', school_id=scds_school.id).first()
        
        if not section7:
            section7 = Section.query.filter_by(name='Section 7', school_id=scds_school.id).first()
            if not section7:
                print("Error: Section 7 not found.")
                return

        print(f"Adding Batch 3 students to {scds_school.name}, {section7.name} (ID: {section7.id})")

        # Load students from JSON
        with open('section7_students_batch3.json', 'r') as f:
            students_data = json.load(f)

        pw_hash = bcrypt.generate_password_hash("hive@1234").decode('utf-8')
        
        added_count = 0
        skipped_count = 0

        for s_data in students_data:
            email = s_data['email']
            name = s_data['name']
            
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"Skipping: User {email} already exists.")
                skipped_count += 1
                continue
            
            user = User(
                school_id=scds_school.id,
                email=email,
                password_hash=pw_hash,
                role='student',
                name=name
            )
            db.session.add(user)
            db.session.flush()
            
            student_profile = Student(
                user_id=user.id,
                section_id=section7.id,
                enrollment_year=2025,
                major="Computer Science"
            )
            db.session.add(student_profile)
            added_count += 1
            print(f"Added student: {name} ({email})")

        db.session.commit()
        print(f"\nFinished! Added {added_count} batch 3 students to Section 7, skipped {skipped_count}.")

if __name__ == "__main__":
    insert_section7_batch3()
