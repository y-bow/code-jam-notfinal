from app import create_app
from app.models import db, User

def update_students_batch3():
    app = create_app()
    with app.app_context():
        # List of corrections for batch 3 (Rows 56-86)
        corrections = [
            # Row 69
            ('prasanthsri.b-29@scds.saiuniversity.edu.in', 'Buragadda Prasanth Sai', 'prasanthsai.b-29@scds.saiuniversity.edu.in'),
            # Row 80
            ('mokshagna.p-29@scds.saiuniversity.edu.in', None, 'mokshagnarao.p-29@scds.saiuniversity.edu.in'),
            # Row 82
            ('maheshreddy.m-29@scds.saiuniversity.edu.in', 'Mamilla Reddy Mahesh Reddy', None),
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
        print(f"\nFinished! Corrected {updated_count} records in batch 3.")

if __name__ == "__main__":
    update_students_batch3()
