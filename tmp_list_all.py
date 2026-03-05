from app import app
from models import TimetableEntry

with app.app_context():
    entries = TimetableEntry.query.filter_by(section_id=2).order_by(TimetableEntry.day, TimetableEntry.start_time).all()
    print(f'Total entries for Section 2: {len(entries)}')
    for e in entries:
        print(f'Day {e.day} | {e.start_time}-{e.end_time} | {e.title}')
