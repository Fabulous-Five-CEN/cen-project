import unittest
from datetime import datetime

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User

test_users = [
    {"email": "amanda@test.com", "password": "password123", "display_name": "Amanda"},
    {"email": "juan@test.com", "password": "password123", "display_name": "Juan"},
    {"email": "mohamed@test.com", "password": "password123", "display_name": "Mohamed"},
]


class SeedUsersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def test_seed_users(self):
        for u in test_users:
            if not User.query.filter_by(email=u["email"]).first():
                hashed_pw = generate_password_hash(u["password"])
                user = User(
                    email=u["email"],
                    password_hash=hashed_pw,
                    display_name=u.get("display_name"),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.session.add(user)
        db.session.commit()

        for u in test_users:
            created = User.query.filter_by(email=u["email"]).first()
            self.assertIsNotNone(created, f"User {u['email']} should exist after seeding")
        print("Test users created successfully!")


if __name__ == "__main__":
    unittest.main()
