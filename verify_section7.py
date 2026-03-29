from app import create_app
from app.models import db, School, Section, Student, User

def verify_section7():
    app = create_app()
    with app.app_context():
        scds = School.query.filter_by(code='SCDS').first()
        section7 = Section.query.filter_by(name='Section 7', school_id=scds.id).first()
        
        student_count = Student.query.filter_by(section_id=section7.id).count()
        print(f"Total students in {scds.name}, {section7.name}: {student_count}")
        
        # List first 5 students
        students = Student.query.filter_by(section_id=section7.id).limit(5).all()
        for s in students:
            print(f"- {s.user.name} ({s.user.email})")

if __name__ == "__main__":
    verify_section7()
