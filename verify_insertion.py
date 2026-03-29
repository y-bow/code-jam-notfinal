from app import create_app
from app.models import db, User, Student, Section

app = create_app()

def verify():
    with app.app_context():
        section = Section.query.filter_by(name='Section 2').first()
        if not section:
            print("Section 2 not found!")
            return
            
        students = Student.query.filter_by(section_id=section.id).all()
        print(f"Total students in Section 2: {len(students)}")
        
        print("\nLast 5 students added:")
        for s in students[-5:]:
            user = User.query.get(s.user_id)
            print(f"- {user.name} ({user.email})")

if __name__ == "__main__":
    verify()
