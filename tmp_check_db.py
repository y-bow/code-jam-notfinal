from app import app
from models import User, Student, TimetableEntry
from datetime import datetime

with app.app_context():
    u = User.query.filter(User.name.like('%Vaibhav%')).first()
    if u:
        s = Student.query.get(u.id)
        if s:
            today = datetime.now().weekday()
            entries = TimetableEntry.query.filter_by(section_id=s.section_id, day=today).all()
            print(f'User: {u.name}, Section ID: {s.section_id}, Day: {today}')
            print(f'Entries count: {len(entries)}')
            for e in entries:
                print(f'- {e.start_time}: {e.title}')
        else:
            print('Student profile not found')
    else:
        print('User not found')
