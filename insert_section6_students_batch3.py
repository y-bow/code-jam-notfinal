import os
from app import create_app
from app.models import db, School, Section, User, Student, bcrypt

app = create_app()

def insert_students():
    with app.app_context():
        # Find schools
        scds_school = School.query.filter_by(code='SCDS').first()
        soai_school = School.query.filter_by(code='SOAI').first()
        
        if not scds_school:
            print("Error: School SCDS not found.")
            return

        # Find the Section (Belongs to SCDS)
        section = Section.query.filter_by(name='Section 6', school_id=scds_school.id).first()
        if not section:
            print("Error: Section 6 not found.")
            return

        print(f"Adding students to Section 6 (ID: {section.id})")

        pw_hash = bcrypt.generate_password_hash("hive@1234").decode('utf-8')

        # (Name, Email, SchoolCode)
        student_data = [
            ("Baira Kushi", "kushi.b-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Kanam Chandu", "chandu.k-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Bakkisetty Tarun", "tarun.b-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Podapati Sasidhar", "sasidhar.p-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Rayi Manvitha Rai", "manvitharaj.r-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Tankasala Geethika", "geethika.t-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Bovilla Meganadh Reddy", "meghanadhreddy.b-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Abhiram Thandra", "abhiram.t-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Vasili Hemal Ankeswar", "hemalankeswar.v-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Ravipati Kouhik Sri Ram", "kowshiksriram.r-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Kesamsetty Shanmukha Lakshmi", "shanmukhalakshmi.k-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Ravipati Rajesh", "rajesh.r-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Maddala Haricharan Reddy", "haricharanreddy.m-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Peddireddy Siva Kumar Reddy", "sivakumarreddy.p-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Chamarthi Karthik Varma", "karthikvarma.c-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Sannareddy Mohitha Reddy", "mohitha.s-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Konakalla Sri Purna Akshith", "puranakshith.k-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Kandrati Tejomai", "tejoamai.k-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Battula Bharath Kumar Reddy", "barathkumar.r-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Meha E", "meha.e-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Thugu Harshavardhan Reddy", "harshavardhan.t1-29@scds.saiuniversity.edu.in", "SCDS"),
            ("J L Dhanush", "dhanush.j-29@scds.saiuniversity.edu.in", "SCDS"),
            ("Tadikela Sandeep Kumar", "sandeepkumar.t-29@soai.saiuniversity.edu.in", "SOAI")
        ]

        added_count = 0
        existing_count = 0

        for name, email, school_code in student_data:
            existing = User.query.filter_by(email=email).first()
            if existing:
                existing_count += 1
                continue

            target_school = scds_school if school_code == "SCDS" else soai_school
            if not target_school:
                print(f"Warning: School {school_code} not found for student {name}. Skipping User creation.")
                continue

            user = User(
                school_id=target_school.id,
                email=email,
                password_hash=pw_hash,
                role='student',
                name=name
            )
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                section_id=section.id,
                enrollment_year=2025,
                major="Computer Science"
            )
            db.session.add(student)
            added_count += 1

        db.session.commit()
        print(f"Finished. Added: {added_count}, Already existed: {existing_count}")

if __name__ == "__main__":
    insert_students()
