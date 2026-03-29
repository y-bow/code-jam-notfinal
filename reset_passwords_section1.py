from app import create_app
from app.models import db, User, Student, Section, School, bcrypt

def reset_passwords():
    app = create_app()
    with app.app_context():
        # Find Section 1
        scds = School.query.filter_by(code='SCDS').first()
        section1 = Section.query.filter_by(name='Section 1', school_id=scds.id).first()
        
        if not section1:
            print("Error: Section 1 not found.")
            return

        print(f"Resetting passwords for all students in {section1.name}...")

        # Find all students in Section 1
        students = Student.query.filter_by(section_id=section1.id).all()
        
        pw_hash = bcrypt.generate_password_hash("hive@1234").decode('utf-8')
        
        updated_count = 0
        for student in students:
            user = student.user
            if user:
                user.password_hash = pw_hash
                updated_count += 1
                # print(f"Reset password for: {user.email}") # Too much output

        db.session.commit()
        print(f"\nFinished! Reset passwords for {updated_count} students in Section 1.")

if __name__ == "__main__":
    reset_passwords()
