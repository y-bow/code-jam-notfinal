from app import create_app
from app.models import db, User, bcrypt

app = create_app()

def reset_all_passwords():
    with app.app_context():
        pw_hash = bcrypt.generate_password_hash("hive@1234").decode('utf-8')
        users = User.query.all()
        count = 0
        for user in users:
            user.password_hash = pw_hash
            count += 1
        db.session.commit()
        print(f"Reset password to hive@1234 for {count} users.")

if __name__ == "__main__":
    reset_all_passwords()
