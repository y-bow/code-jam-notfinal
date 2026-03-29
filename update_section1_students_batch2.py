from app import create_app
from app.models import db, User

def update_students_batch2():
    app = create_app()
    with app.app_context():
        # List of corrections for batch 2 (Rows 28-55)
        corrections = [
            # Row 29
            ('lasyagamapriya.k-29@scds.saiuniversity.edu.in', 'Kasya Lasya Gana Priya', 'lasyaganapriya.k-29@scds.saiuniversity.edu.in'),
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
        print(f"\nFinished! Corrected {updated_count} records in batch 2.")

if __name__ == "__main__":
    update_students_batch2()
