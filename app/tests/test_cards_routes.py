import unittest

from app import create_app


class CardsRoutesTestCase(unittest.TestCase):
    """sanity checks for the cards endpoints."""

    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def test_create_card_requires_fields(self):
        response = self.client.post("/cards/new", json={"english_text": "hola"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_auto_translate_rejects_bad_direction(self):
        response = self.client.post(
            "/cards/cards/auto-translate",
            json={"text": "", "direction": "invalid"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
