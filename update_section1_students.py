from app import create_app
from app.models import db, User, Student

def update_students():
    app = create_app()
    with app.app_context():
        # List of corrections
        # Format: (old_email, new_name, new_email)
        # If new_email is None, it won't be updated.
        # If new_name is None, it won't be updated.
        corrections = [
            # Row 5 - Spelling
            ('balaaditya.t-29@scds.saiuniversity.edu.in', 'Balaaditya T', None),
            # Row 6 - Email fix
            ('shilpasharma.s-29@scds.saiuniversity.edu.in', 'Shilpa Sharma', 'shilpasatish.s-29@scds.saiuniversity.edu.in'),
            # Row 13 - Email fix
            ('sreeasaitany.a-29@scds.saiuniversity.edu.in', 'Aitha Sree Sai Tanay', 'sreesaitanay.a-29@scds.saiuniversity.edu.in'),
            # Row 20 - Spelling
            ('sandhya.a-29@scds.saiuniversity.edu.in', 'Avula Disny Sandhya', None),
            # Row 24 - Full name
            ('hemasree.r-29@scds.saiuniversity.edu.in', 'Randhi Hemasree', None),
        ]

        updated_count = 0
        for old_email, new_name, new_email in corrections:
            user = User.query.filter_by(email=old_email).first()
            if not user:
                print(f"⏩ User {old_email} not found. Skipping.")
                continue
            
            if new_name:
                print(f"Updating name for {user.email}: {user.name} -> {new_name}")
                user.name = new_name
            
            if new_email:
                print(f"Updating email for {user.name}: {user.email} -> {new_email}")
                user.email = new_email
            
            updated_count += 1

        db.session.commit()
        print(f"\nFinished! Corrected {updated_count} records.")

if __name__ == "__main__":
    update_students()
