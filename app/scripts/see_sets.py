import os
import unittest
from typing import Dict

import requests
from dotenv import load_dotenv

load_dotenv()

# Config
BACKEND_HOST = os.environ.get("BACKEND_HOST", "http://localhost")
APP_PORT = os.environ.get("APP_PORT", "8000")
BASE_URL = f"{BACKEND_HOST}:{APP_PORT}"
SEED_EMAIL = os.environ.get("SEED_EMAIL", "amanda@test.com")
SEED_PASSWORD = os.environ.get("SEED_PASSWORD", "password123")

PRACTICE_SET = {
    "name": "Practice Verification Set",
    "description": "Set created by see_sets.py integration test",
}
PRACTICE_CARDS = [
    {"english_text": "Water", "spanish_text": "El agua"},
    {"english_text": "Food", "spanish_text": "La comida"},
    {"english_text": "Help", "spanish_text": "Ayuda"},
]


class PracticeSetIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        login_resp = cls.session.post(
            f"{BASE_URL}/auth/login",
            json={"email": SEED_EMAIL, "password": SEED_PASSWORD},
        )
        if login_resp.status_code != 200:
            raise AssertionError(
                f"Login failed for {SEED_EMAIL}: {login_resp.status_code} {login_resp.text}"
            )
        cls.user = login_resp.json().get("user")

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def _create_set(self, payload: Dict) -> int:
        resp = self.session.post(f"{BASE_URL}/sets/new", json=payload)
        self.assertEqual(resp.status_code, 201, f"Failed to create set: {resp.text}")
        return resp.json()["set"]["id"]

    def _create_card(self, payload: Dict) -> int:
        resp = self.session.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(resp.status_code, 201, f"Failed to create card: {resp.text}")
        return resp.json()["card"]["id"]

    def _assign_cards_to_set(self, set_id, card_ids):
        resp = self.session.post(
            f"{BASE_URL}/sets/add_card/{set_id}", json={"card_ids": card_ids}
        )
        self.assertEqual(
            resp.status_code,
            200,
            f"Failed to add cards to set {set_id}: {resp.status_code} {resp.text}",
        )

    def test_retrieve_cards_for_set(self):
        set_id = self._create_set(PRACTICE_SET)
        card_ids = [self._create_card(card) for card in PRACTICE_CARDS]
        self._assign_cards_to_set(set_id, card_ids)

        resp = self.session.get(f"{BASE_URL}/practice/set/{set_id}")
        self.assertEqual(
            resp.status_code, 200, f"Unexpected response: {resp.status_code}, {resp.text}"
        )
        data = resp.json()
        self.assertIsInstance(data, list, "List of cards should be returned")
        self.assertGreaterEqual(len(data), len(PRACTICE_CARDS))

        if data:
            print(f"\nCards in set {set_id}:")
            for card in data:
                print(f"ID: {card['id']} | EN: {card['english_text']} | ES: {card['spanish_text']}")

        sample = data[0]
        self.assertIn("id", sample)
        self.assertIn("spanish_text", sample)
        self.assertIn("english_text", sample)

    def test_invalid_set_id_returns_error(self):
        invalid_set_id = 999999
        resp = self.session.get(f"{BASE_URL}/practice/set/{invalid_set_id}")
        self.assertIn(
            resp.status_code,
            [404, 400],
            f"Expected 404/400, got {resp.status_code}",
        )
        data = resp.json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
