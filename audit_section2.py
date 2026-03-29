from app import create_app
from app.models import db, User, Student, Section

app = create_app()

def audit():
    with app.app_context():
        section = Section.query.filter_by(name='Section 2').first()
        students = Student.query.filter_by(section_id=section.id).all()
        print(f"Total in Section 2: {len(students)}")
        
        for s in students:
            user = User.query.get(s.user_id)
            print(f"- {user.email}")

if __name__ == "__main__":
    audit()
