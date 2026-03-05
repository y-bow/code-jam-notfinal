from app import app
from models import User, Student, Section

with app.app_context():
    u = User.query.filter(User.name.like('%Vaibhav%')).first()
    if u:
        s = Student.query.get(u.id)
        if s:
            sec = Section.query.get(s.section_id)
            print(f'User: {u.name}, School ID: {u.school_id}, Section ID: {s.section_id}, Section School ID: {sec.school_id}')
        else:
            print('Student profile not found')
    else:
        print('User not found')
