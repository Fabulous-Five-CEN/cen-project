# RUN THIS FILE AFTER SUCCESSFULLY RUNNING SEED_SETS.PY, MODIFY THE SET_ID WITH WHATEVER IT SHOWS UP AS IN THE DATABASE FOR YOU

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
SET_ID = 31  # The set we want to check


class PracticeSetIntegrationTests(unittest.TestCase):
    def test_retrieve_cards_for_set(self):
        url = f"{BASE_URL}/practice/{SET_ID}"
        params = {"user_id": USER_ID}

        resp = requests.get(url, params=params)
        self.assertEqual(resp.status_code, 200, f"Unexpected response: {resp.status_code}, {resp.text}")
        print("method accessed")
        data = resp.json()
        self.assertIsInstance(data, list, "List of card sshould be returned")

        if data:
            print(f"\nCards in set {SET_ID}:")
            for card in data:
                print(f"ID: {card['id']} | EN: {card['english_text']} | ES: {card['spanish_text']}")
        else:
            print(f"\nNo cards found in set {SET_ID}")

        if data:
            sample = data[0]
            self.assertIn("id", sample)
            self.assertIn("spanish_text", sample)
            self.assertIn("english_text", sample)
        else:
            print(f"No cards returned — check if set {SET_ID} is valid in database")

    def test_invalid_set_id_returns_error(self):
        """Ensure invalid set_id returns a 404 error."""
        invalid_set_id = 999999
        url = f"{BASE_URL}/practice/{invalid_set_id}"
        params = {"user_id": USER_ID}

        resp = requests.get(url, params=params)
        self.assertIn(resp.status_code, [404, 400], f"Expected 404/400, got {resp.status_code}")
        data = resp.json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
