import os
import unittest
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

# Config
BACKEND_HOST = os.environ.get("BACKEND_HOST", "http://localhost")
APP_PORT = os.environ.get("APP_PORT", "8000")
BASE_URL = f"{BACKEND_HOST}:{APP_PORT}"
SEED_EMAIL = os.environ.get("SEED_EMAIL", "amanda@test.com")
SEED_PASSWORD = os.environ.get("SEED_PASSWORD", "password123")

SET_DEFINITIONS: Dict[str, List[Dict[str, str]]] = {
    "Household Objects": [
        {"english_text": "House", "spanish_text": "La casa"},
        {"english_text": "Table", "spanish_text": "La mesa"},
        {"english_text": "Chair", "spanish_text": "La silla"},
        {"english_text": "Desk", "spanish_text": "El escritorio"},
        {"english_text": "Bed", "spanish_text": "La cama"},
        {"english_text": "Kitchen", "spanish_text": "La cocina"},
    ],
    "School Vocabulary": [
        {"english_text": "School", "spanish_text": "La escuela"},
        {"english_text": "Teacher", "spanish_text": "El maestro / La maestra"},
        {"english_text": "Pen", "spanish_text": "El bolígrafo"},
        {"english_text": "Pencil", "spanish_text": "El lápiz"},
        {"english_text": "Chair", "spanish_text": "La silla"},
        {"english_text": "Desk", "spanish_text": "El escritorio"},
    ],
}


class SeedDatabase(unittest.TestCase):
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
        cls.user_id = cls.user.get("id") if cls.user else None
        if not cls.user_id:
            raise AssertionError("Authenticated user id missing from login response")

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def _create_set(self, name: str, description: str = "") -> int:
        payload = {"name": name, "description": description}
        resp = self.session.post(f"{BASE_URL}/sets/new", json=payload)
        self.assertEqual(
            resp.status_code, 201, f"Failed to create set '{name}': {resp.text}"
        )
        return resp.json()["set"]["id"]

    def _create_card(self, english: str, spanish: str) -> int:
        payload = {"english_text": english, "spanish_text": spanish}
        resp = self.session.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(
            resp.status_code,
            201,
            f"Failed to create card '{english} / {spanish}': {resp.text}",
        )
        return resp.json()["card"]["id"]

    def _assign_cards_to_set(self, set_id: int, card_ids: List[int]) -> None:
        resp = self.session.post(
            f"{BASE_URL}/sets/add_card/{set_id}", json={"card_ids": card_ids}
        )
        self.assertEqual(
            resp.status_code,
            200,
            f"Failed to add cards to set {set_id}: {resp.status_code} {resp.text}",
        )

    def _print_seeded_sets(self, set_ids: List[int]) -> None:
        """Query the API for each set_id and print the cards."""
        for set_id in set_ids:
            resp = self.session.get(f"{BASE_URL}/sets/{set_id}")
            if resp.status_code != 200:
                print(f"Failed to fetch set {set_id}: {resp.text}")
                continue

            data = resp.json()
            set_name = data.get("name")
            cards = data.get("cards", [])

            print(f"\nSet ID: {set_id}, Name: {set_name}, Cards ({len(cards)}):")
            if not cards:
                print("  No cards in this set.")
                continue

            for card in cards:
                print(
                    f"  Card ID: {card['id']}, English: {card['english_text']}, Spanish: {card['spanish_text']}"
                )

    def test_seed_data(self):
        created_sets = []
        for set_name, cards in SET_DEFINITIONS.items():
            set_id = self._create_set(set_name, f"Auto-seeded: {set_name}")
            card_ids = [self._create_card(c["english_text"], c["spanish_text"]) for c in cards]
            self._assign_cards_to_set(set_id, card_ids)
            created_sets.append(set_id)

        print("Seed data created successfully.")
        self._print_seeded_sets(created_sets)


if __name__ == "__main__":
    unittest.main()
