from dotenv import load_dotenv
load_dotenv()
import os
import unittest
import requests

APP_PORT = os.environ.get("APP_PORT", "8025")
BACKEND_HOST = os.environ.get("BACKEND_HOST", "http://localhost")
BASE_URL = f"{BACKEND_HOST}:{APP_PORT}"
USER_ID = int(os.environ.get("TEST_USER_ID", "2"))


class PracticeIntegrationWithSeed(unittest.TestCase):
    def setUp(self):
        self.created_set_ids = []
        self.created_card_ids = []

    def tearDown(self):
        for set_id in self.created_set_ids:
            requests.delete(f"{BASE_URL}/sets/delete/{set_id}")
        for card_id in self.created_card_ids:
            requests.delete(f"{BASE_URL}/cards/delete/{card_id}")

    def _create_set(self, name, description=""):
        payload = {"name": name, "description": description, "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/sets/new", json=payload)
        self.assertEqual(resp.status_code, 201, f"Failed to create set. Response: {resp.text}")
        set_id = resp.json()["set"]["id"]
        self.created_set_ids.append(set_id)
        return set_id

    def _create_card(self, english, spanish):
        payload = {"english_text": english, "spanish_text": spanish, "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(resp.status_code, 201, f"Failed to create card. Response: {resp.text}")
        card_id = resp.json()["card"]["id"]
        self.created_card_ids.append(card_id)
        return card_id

    def test_seed_and_practice(self):

        # CREATE SETS WITH OVERLAPPING CARDS
        set1_id = self._create_set("Household Objects", "objects you would find in a house")
        set2_id = self._create_set("School Vocabulary", "objects and concepts in a school")

        card1_id = self._create_card("House", "La casa")
        card2_id = self._create_card("Table", "La mesa")
        card3_id = self._create_card("Chair", "La silla")
        card4_id = self._create_card("Desk", "El escritorio")
        card5_id = self._create_card("Bed", "La cama")
        card6_id = self._create_card("Kitchen", "La cocina")

        card7_id = self._create_card("School", "La escuela")
        card8_id = self._create_card("Teacher", "El maestro / La maestra")
        card9_id = self._create_card("Pen", "El bolígrafo")
        card10_id = self._create_card("Pencil", "El lápiz")

        # ADD TO SETS
        requests.post(f"{BASE_URL}/sets/add_card/{set1_id}", json={"card_ids": [card1_id, card2_id, card3_id, card4_id, card5_id, card6_id]})
        requests.post(f"{BASE_URL}/sets/add_card/{set2_id}", json={"card_ids": [card3_id, card4_id, card7_id, card8_id, card9_id, card10_id]})

        # PRINT DATA TO CONFIRM
        for set_id in [set1_id, set2_id]:
            url = f"{BASE_URL}/practice/{set_id}"
            params = {"user_id": USER_ID}
            resp = requests.get(url, params=params)
            self.assertEqual(resp.status_code, 200, f"Unexpected response: {resp.status_code}, {resp.text}")
            data = resp.json()
            self.assertIsInstance(data, list)
            print(f"\nCards in set {set_id}:")
            for card in data:
                print(f"  ID: {card['id']} | EN: {card['english_text']} | ES: {card['spanish_text']}")


    # MAKE SURE AN INVALID SET ID IS REJECTED
    def test_invalid_set_id(self):
        invalid_set_id = 999999
        url = f"{BASE_URL}/practice/{invalid_set_id}"
        params = {"user_id": USER_ID}
        resp = requests.get(url, params=params)
        self.assertIn(resp.status_code, [404, 400])
        data = resp.json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
