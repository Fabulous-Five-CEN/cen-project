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


class SetIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.created_set_ids = []
        self.created_card_ids = []

    def tearDown(self):
        for set_id in self.created_set_ids:
            requests.delete(f"{BASE_URL}/sets/delete/{set_id}")
        
        for card_id in self.created_card_ids:
            requests.delete(f"{BASE_URL}/cards/delete/{card_id}")

    def _create_set(self, name="Test Set", description="A temporary set for testing."):
        payload = {"name": name, "description": description, "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/sets/new", json=payload)
        self.assertEqual(resp.status_code, 201, f"Failed to create helper set. Response: {resp.text}")
        set_id = resp.json()["set"]["id"]
        self.created_set_ids.append(set_id)
        return set_id

    def _create_card(self, english="test word", spanish="palabra de prueba"):
        payload = {"english_text": english, "spanish_text": spanish, "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(resp.status_code, 201, f"Failed to create helper card. Response: {resp.text}")
        card_id = resp.json()["card"]["id"]
        self.created_card_ids.append(card_id)
        return card_id

    def test_create_set_success(self):
        payload = {
            "name": "Kitchen Vocabulary",
            "description": "Words for things found in the kitchen.",
            "user_id": USER_ID
        }
        resp = requests.post(f"{BASE_URL}/sets/new", json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["set"]["name"], "Kitchen Vocabulary")
        self.created_set_ids.append(data["set"]["id"])

    def test_create_set_missing_name_fails(self):
        payload = {"description": "A set without a name.", "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/sets/new", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_edit_set_success(self):
        set_id = self._create_set()
        update_payload = {"name": "Updated Set Name", "description": "Updated description."}

        resp = requests.put(f"{BASE_URL}/sets/edit/{set_id}", json=update_payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["set"]["name"], "Updated Set Name")

    def test_delete_set_success(self):
        set_id = self._create_set()

        resp = requests.delete(f"{BASE_URL}/sets/delete/{set_id}")
        self.assertEqual(resp.status_code, 200)
        get_resp = requests.get(f"{BASE_URL}/sets/{set_id}")
        self.assertEqual(get_resp.status_code, 404)
        self.created_set_ids.remove(set_id)

    def test_get_all_sets_for_user(self):
        self._create_set(name="Set One")
        self._create_set(name="Set Two")
        resp = requests.get(f"{BASE_URL}/sets/", params={"user_id": USER_ID})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        set_names = {item['name'] for item in data}
        self.assertIn("Set One", set_names)
        self.assertIn("Set Two", set_names)

    def test_add_card_to_set_success(self):
        set_id = self._create_set()
        card_id = self._create_card()
        payload = {"card_ids": [card_id]} 

        resp = requests.post(f"{BASE_URL}/sets/add_card/{set_id}", json=payload)
        self.assertEqual(resp.status_code, 200)
        details_resp = requests.get(f"{BASE_URL}/sets/{set_id}")
        self.assertEqual(details_resp.status_code, 200)
        card_ids_in_set = [card['id'] for card in details_resp.json()['cards']]
        self.assertIn(card_id, card_ids_in_set)

    def test_remove_card_from_set_success(self):
        set_id = self._create_set()
        card_id = self._create_card()
  
        requests.post(f"{BASE_URL}/sets/add_card/{set_id}", json={"card_ids": [card_id]})
        
        remove_payload = {"card_id": card_id}

        resp = requests.post(f"{BASE_URL}/sets/delete_card/{set_id}", json=remove_payload)
        self.assertEqual(resp.status_code, 200)
        
        details_resp = requests.get(f"{BASE_URL}/sets/{set_id}")
        self.assertEqual(details_resp.status_code, 200)
        self.assertEqual(len(details_resp.json()['cards']), 0)


if __name__ == "__main__":
    unittest.main()