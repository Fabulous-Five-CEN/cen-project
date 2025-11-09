from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

test_users = [
    {"email": "amanda@test.com", "password": "password123", "display_name": "Amanda"},
    {"email": "juan@test.com", "password": "password123", "display_name": "Juan"},
    {"email": "mohamed@test.com", "password": "password123", "display_name": "Mohamed"},
]

def seed_users():
    app = create_app()
    with app.app_context():
        for u in test_users:
            if not User.query.filter_by(email=u["email"]).first():
                hashed_pw = generate_password_hash(u["password"])
                user = User(
                    email=u["email"],
                    password_hash=hashed_pw,
                    display_name=u.get("display_name"),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(user)
        db.session.commit()
        print("Test users created successfully!")

if __name__ == "__main__":
    seed_users()
