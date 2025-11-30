from dotenv import load_dotenv
load_dotenv()
import unittest
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User


class CardsRoutesTestCase(unittest.TestCase):
    """sanity checks for the cards endpoints."""

    def setUp(self):
        config_override = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False},
            },
        }
        self.app = create_app(config_override)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.password = "Password123!"
        self.user = User(
            email="routes@test.com",
            password_hash=generate_password_hash(self.password),
            display_name="Routes User",
        )
        db.session.add(self.user)
        db.session.commit()
        self._login()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login(self):
        self.client.post(
            "/auth/login",
            json={"email": self.user.email, "password": self.password},
        )

    def test_create_card_requires_fields(self):
        response = self.client.post("/cards/new", json={"english_text": "hola"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_auto_translate_rejects_bad_direction(self):
        response = self.client.post(
            "/cards/auto-translate",
            json={"text": "", "direction": "invalid"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
