import os
import time
import unittest

import requests


APP_PORT = os.environ.get("APP_PORT", "8025")
BACKEND_HOST = os.environ.get("BACKEND_HOST", "http://localhost")
BASE_URL = os.environ.get("CARDS_BASE_URL", f"{BACKEND_HOST}:{APP_PORT}")
USER_ID = int(os.environ.get("TEST_USER_ID", "2"))  # Valid user_id in db


class CardIntegrationTests(unittest.TestCase):
    def setUp(self):
        """Set up a list to track created cards for cleanup."""
        self.created_ids = []

    def tearDown(self):
        """Clean up cards after each test."""
        for card_id in self.created_ids:
            requests.delete(f"{BASE_URL}/cards/delete/{card_id}")

    # TC001: Create card successfully
    def test_create_card_success(self):
        payload = {
            "english_text": "apple",
            "spanish_text": "la manzana",
            "notes": "basic food",
            "is_starred": False,
            "user_id": USER_ID
        }
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(resp.status_code, 201)
        card_id = resp.json()["card"]["id"]
        self.created_ids.append(card_id)
        self.assertEqual(resp.json()["card"]["english_text"], "apple")

    # TC002A: Missing English
    def test_create_card_missing_english(self):
        payload = {"spanish_text": "perro", "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(resp.status_code, 400)

    # TC002B: Missing Spanish
    def test_create_card_missing_spanish(self):
        payload = {"english_text": "dog", "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(resp.status_code, 400)

    # TC002C: Missing User
    def test_create_card_missing_user(self):
        payload = {"english_text": "tree", "spanish_text": "árbol"}
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(resp.status_code, 400)

    # TC003: Invalid User ID
    def test_create_card_invalid_user(self):
        payload = {"english_text": "cat", "spanish_text": "el gato", "user_id": 9999}
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)
        self.assertEqual(resp.status_code, 404)

    # TC004: English -> Spanish Auto-translate
    def test_auto_translate_en_to_es(self):
        resp = requests.post(f"{BASE_URL}/cards/auto-translate", json={
            "text": "dog",
            "direction": "english_to_spanish"
        })
       
        self.assertEqual(resp.status_code, 200)
        self.assertIn("translated_text", resp.json())
        time.sleep(1)

    # TC005: Spanish -> English Auto-translate
    def test_auto_translate_es_to_en(self):
        resp = requests.post(f"{BASE_URL}/cards/auto-translate", json={
            "text": "tengo",
            "direction": "spanish_to_english"
        })
        print("Status code:", resp.status_code)
        try:
            print("Response JSON:", resp.json())
        except Exception as e:
            print("Failed to parse JSON:", e)
            print("Raw response text:", resp.text)
        print("method reached")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("translated_text", resp.json())



        # TC006: Edit a card
    def test_edit_card(self):
        # create card
        payload = {"english_text": "dog", "spanish_text": "el perro", "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)

        # debug: print full response from creation
        print("Create card response status:", resp.status_code)
        print("Create card response JSON:", resp.text)

        card_id = resp.json()["card"]["id"]
        self.created_ids.append(card_id)

        # edit card
        update_payload = {"english_text": "puppy"}
        edit_resp = requests.put(f"{BASE_URL}/cards/edit/{card_id}", json=update_payload)

        # debug: print full response from edit
        print("Edit card response status:", edit_resp.status_code)
        print("Edit card response JSON:", edit_resp.text)

        self.assertEqual(edit_resp.status_code, 200)
        self.assertEqual(edit_resp.json()["card"]["english_text"], "puppy")


    # TC007: Delete a card
    def test_delete_card(self):
        payload = {"english_text": "temp", "spanish_text": "temporal", "user_id": USER_ID}
        resp = requests.post(f"{BASE_URL}/cards/new", json=payload)
        card_id = resp.json()["card"]["id"]

        del_resp = requests.delete(f"{BASE_URL}/cards/delete/{card_id}")
        self.assertEqual(del_resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
