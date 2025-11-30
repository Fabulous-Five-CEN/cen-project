import os
import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User


class LectoTranslateRouteTests(unittest.TestCase):
    def setUp(self):
        os.environ.setdefault("RAPIDAPI_KEY", "test-rapidapi-key")
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
            email="lecto@test.com",
            password_hash=generate_password_hash(self.password),
            display_name="Lecto User",
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

    def _mock_translation(self, mock_post, translated_text):
        fake_response = MagicMock()
        fake_response.json.return_value = {
            "translations": [{"translated": [translated_text]}],
            "translated_characters": len(translated_text),
        }
        fake_response.raise_for_status = MagicMock()
        mock_post.return_value = fake_response

    @patch("app.cards.routes.requests.post")
    def test_auto_translate_english_to_spanish(self, mock_post):
        self._mock_translation(mock_post, "El perro")

        resp = self.client.post(
            "/cards/auto-translate",
            json={"text": "dog", "direction": "english_to_spanish"},
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["translated_text"], "El perro")
        args, kwargs = mock_post.call_args
        self.assertIn("rapidapi", args[0])
        self.assertEqual(kwargs["json"]["texts"], ["dog"])

    @patch("app.cards.routes.requests.post")
    def test_auto_translate_spanish_to_english(self, mock_post):
        self._mock_translation(mock_post, "I have")

        resp = self.client.post(
            "/cards/auto-translate",
            json={"text": "tengo", "direction": "spanish_to_english"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["translated_text"], "I have")

    def test_auto_translate_requires_valid_direction(self):
        resp = self.client.post(
            "/cards/auto-translate", json={"text": "hola", "direction": "invalid"}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())


if __name__ == "__main__":
    unittest.main()
