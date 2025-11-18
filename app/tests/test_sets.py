import unittest

from sqlalchemy.pool import StaticPool

from app import create_app, db
from app.models import Card, SetTable, User


class SetRouteTests(unittest.TestCase):
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
            email="sets@test.com",
            password_hash="hashed",
            display_name="Set User",
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_set_direct(self, name="Test Set", description="temp set"):
        set_obj = SetTable(name=name, description=description, user_id=self.user.id)
        db.session.add(set_obj)
        db.session.commit()
        return set_obj

    def _create_card_direct(self, english="test word", spanish="palabra de prueba"):
        card = Card(
            english_text=english,
            spanish_text=spanish,
            user_id=self.user.id,
        )
        db.session.add(card)
        db.session.commit()
        return card

    def test_create_set_success(self):
        payload = {
            "name": "Kitchen Vocabulary",
            "description": "Words for things found in the kitchen.",
            "user_id": self.user.id,
        }
        resp = self.client.post("/sets/new", json=payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()["set"]["name"], "Kitchen Vocabulary")

    def test_create_set_missing_name_fails(self):
        payload = {"description": "A set without a name.", "user_id": self.user.id}
        resp = self.client.post("/sets/new", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_edit_set_success(self):
        set_obj = self._create_set_direct()
        update_payload = {
            "name": "Updated Set Name",
            "description": "Updated description.",
        }

        resp = self.client.put(f"/sets/edit/{set_obj.id}", json=update_payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["set"]["name"], "Updated Set Name")

    def test_delete_set_success(self):
        set_obj = self._create_set_direct()

        resp = self.client.delete(f"/sets/delete/{set_obj.id}")
        self.assertEqual(resp.status_code, 200)
        get_resp = self.client.get(f"/sets/{set_obj.id}")
        self.assertEqual(get_resp.status_code, 404)

    def test_get_all_sets_for_user(self):
        self._create_set_direct(name="Set One")
        self._create_set_direct(name="Set Two")
        resp = self.client.get(f"/sets/?user_id={self.user.id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        set_names = {item["name"] for item in data}
        self.assertIn("Set One", set_names)
        self.assertIn("Set Two", set_names)

    def test_add_card_to_set_success(self):
        set_obj = self._create_set_direct()
        card = self._create_card_direct()
        payload = {"card_ids": [card.id]}

        resp = self.client.post(f"/sets/add_card/{set_obj.id}", json=payload)
        self.assertEqual(resp.status_code, 200)
        details_resp = self.client.get(f"/sets/{set_obj.id}")
        self.assertEqual(details_resp.status_code, 200)
        card_ids_in_set = [card_json["id"] for card_json in details_resp.get_json()["cards"]]
        self.assertIn(card.id, card_ids_in_set)

    def test_remove_card_from_set_success(self):
        set_obj = self._create_set_direct()
        card = self._create_card_direct()

        self.client.post(f"/sets/add_card/{set_obj.id}", json={"card_ids": [card.id]})

        remove_payload = {"card_id": card.id}
        resp = self.client.post(f"/sets/delete_card/{set_obj.id}", json=remove_payload)
        self.assertEqual(resp.status_code, 200)

        details_resp = self.client.get(f"/sets/{set_obj.id}")
        self.assertEqual(details_resp.status_code, 200)
        self.assertEqual(len(details_resp.get_json()["cards"]), 0)


if __name__ == "__main__":
    unittest.main()
