from app import create_app
from app.models import db, User, Student, Section, School, bcrypt

def verify_passwords():
    app = create_app()
    with app.app_context():
        # Find Section 1
        scds = School.query.filter_by(code='SCDS').first()
        section1 = Section.query.filter_by(name='Section 1', school_id=scds.id).first()
        
        # Find all students in Section 1
        students = Student.query.filter_by(section_id=section1.id).all()
        
        all_ok = True
        for student in students:
            user = student.user
            if not bcrypt.check_password_hash(user.password_hash, "hive@1234"):
                print(f"❌ Password mismatch for: {user.email}")
                all_ok = False
        
        if all_ok:
            print(f"All {len(students)} students in Section 1 have the password 'hive@1234'.")
        else:
            print("Error: Some passwords do not match.")

if __name__ == "__main__":
    verify_passwords()
