from dotenv import load_dotenv
load_dotenv()
import os
import unittest
import requests

# Config
APP_PORT = os.environ.get("APP_PORT", "8025")
BACKEND_HOST = os.environ.get("BACKEND_HOST", "http://localhost")
BASE_URL = f"{BACKEND_HOST}:{APP_PORT}"
USER_ID = int(os.environ.get("TEST_USER_ID", "2"))


class SeedDatabase(unittest.TestCase):
    def print_seeded_sets(self, set_ids):
            """Query the API for each set_id and print the cards."""
            for set_id in set_ids:
                resp = requests.get(f"{BASE_URL}/sets/{set_id}")
                if resp.status_code != 200:
                    print(f"Failed to fetch set {set_id}: {resp.text}")
                    continue

                data = resp.json()
                set_name = data.get("name")
                cards = data.get("cards", [])

                print(f"\nSet ID: {set_id}, Name: {set_name}, Cards ({len(cards)}):")
                if not cards:
                    print("  No cards in this set.")
                else:
                    for card in cards:
                        print(f"  Card ID: {card['id']}, English: {card['english_text']}, Spanish: {card['spanish_text']}")


    def _create_set(self, name, description=""):
        payload = {"name": name, "description": description, "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/sets/new", json=payload)
        self.assertEqual(resp.status_code, 201, f"Failed to create set. Response: {resp.text}")
        return resp.json()["set"]["id"]

    def _create_card(self, english, spanish):
        payload = {"english_text": english, "spanish_text": spanish, "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(resp.status_code, 201, f"Failed to create card. Response: {resp.text}")
        return resp.json()["card"]["id"]

    def test_seed_data(self):
        # sets 
        set1_id = self._create_set("Household Objects", "objects you would find in a house")
        set2_id = self._create_set("School Vocabulary", "objects and concepts in a school")

        # household objects
        card1_id = self._create_card("House", "la casa")
        card2_id = self._create_card("Table", "La mesa")
        card3_id = self._create_card("Chair", "La silla")
        card4_id = self._create_card("Desk", "El escritorio")
        card5_id = self._create_card("Bed", "La cama")
        card6_id = self._create_card("Kitchen", "La cocina")

        # school
        card7_id = self._create_card("School", "La Escuela")
        card8_id = self._create_card("Teacher", "El Maestro / La Maestra")
        card9_id = self._create_card("Pen", "El Bolígrafo")
        card10_id = self._create_card("Penicl", "El lápiz")

        # put desk and chair in both sets

        # Add cards to sets with some overlap
        requests.post(f"{BASE_URL}/sets/add_card/{set1_id}", json={"card_ids": [card1_id, card2_id, card3_id, card4_id, card5_id, card6_id]})
        requests.post(f"{BASE_URL}/sets/add_card/{set2_id}", json={"card_ids": [card3_id, card4_id, card7_id, card8_id, card9_id, card10_id]})

        print("Seed data created successfully:")
   

        self.print_seeded_sets([set1_id, set2_id])


if __name__ == "__main__":
    unittest.main()
