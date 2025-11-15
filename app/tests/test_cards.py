import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.pool import StaticPool

from app import create_app, db
from app.models import Card, User


class CardIntegrationTests(unittest.TestCase):
    """Exercise the cards blueprint using the Flask test client instead of HTTP calls."""

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

        self.user = User(
            email="tester@example.com",
            password_hash="hashed-password",
            display_name="Tester",
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_card(self, english_text="dog", spanish_text="el perro", notes=""):
        card = Card(
            english_text=english_text,
            spanish_text=spanish_text,
            notes=notes,
            user_id=self.user.id,
        )
        db.session.add(card)
        db.session.commit()
        return card

    def _mock_translation(self, mock_post, translated_text):
        fake_response = MagicMock()
        fake_response.json.return_value = {
            "translations": [{"translated": [translated_text]}],
            "translated_characters": len(translated_text),
        }
        fake_response.raise_for_status = MagicMock()
        mock_post.return_value = fake_response

    def test_create_card_success(self):
        payload = {
            "english_text": "apple",
            "spanish_text": "la manzana",
            "notes": "basic food",
            "is_starred": False,
            "user_id": self.user.id,
        }
        resp = self.client.post("/cards/new", json=payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()["card"]["english_text"], "apple")

    def test_create_card_missing_english(self):
        payload = {"spanish_text": "perro", "user_id": self.user.id}
        resp = self.client.post("/cards/new", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_create_card_missing_spanish(self):
        payload = {"english_text": "dog", "user_id": self.user.id}
        resp = self.client.post("/cards/new", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_create_card_missing_user(self):
        payload = {"english_text": "tree", "spanish_text": "árbol"}
        resp = self.client.post("/cards/new", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_create_card_invalid_user(self):
        payload = {
            "english_text": "cat",
            "spanish_text": "el gato",
            "user_id": self.user.id + 999,
        }
        resp = self.client.post("/cards/new", json=payload)
        self.assertEqual(resp.status_code, 404)

    @patch("app.cards.routes.requests.post")
    def test_auto_translate_en_to_es(self, mock_post):
        self._mock_translation(mock_post, "el perro")
        resp = self.client.post(
            "/cards/auto-translate",
            json={"text": "dog", "direction": "english_to_spanish"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["translated_text"], "el perro")

    @patch("app.cards.routes.requests.post")
    def test_auto_translate_es_to_en(self, mock_post):
        self._mock_translation(mock_post, "I have")
        resp = self.client.post(
            "/cards/auto-translate",
            json={"text": "tengo", "direction": "spanish_to_english"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["translated_text"], "I have")

    def test_edit_card(self):
        card = self._create_card()
        update_payload = {"english_text": "puppy"}
        edit_resp = self.client.put(f"/cards/edit/{card.id}", json=update_payload)
        self.assertEqual(edit_resp.status_code, 200)
        self.assertEqual(edit_resp.get_json()["card"]["english_text"], "puppy")

    def test_delete_card(self):
        card = self._create_card(english_text="temp", spanish_text="temporal")
        del_resp = self.client.delete(f"/cards/delete/{card.id}")
        self.assertEqual(del_resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
