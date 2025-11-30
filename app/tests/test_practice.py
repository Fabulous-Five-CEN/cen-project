import unittest

from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Card, PracticeHistory, SetTable, User


class PracticeRouteTests(unittest.TestCase):
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

        self.password = "Password123!"
        self.user = User(
            email="practice@test.com",
            password_hash=generate_password_hash(self.password),
            display_name="Practice User",
        )
        db.session.add(self.user)
        db.session.commit()
        self._login()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login(self):
        self.client.post(
            "/auth/login",
            json={"email": self.user.email, "password": self.password},
        )

    def _create_card(self, english, spanish):
        card = Card(
            english_text=english,
            spanish_text=spanish,
            user_id=self.user.id,
        )
        db.session.add(card)
        db.session.commit()
        return card

    def _create_set(self, name, description="", cards=None):
        set_obj = SetTable(
            name=name,
            description=description,
            user_id=self.user.id,
        )
        db.session.add(set_obj)
        if cards:
            set_obj.cards.extend(cards)
        db.session.commit()
        return set_obj

    def test_practice_returns_cards_for_specific_set(self):
        common_cards = [
            self._create_card("House", "La casa"),
            self._create_card("Chair", "La silla"),
        ]
        household_cards = common_cards + [
            self._create_card("Kitchen", "La cocina"),
            self._create_card("Table", "La mesa"),
        ]
        school_cards = common_cards + [
            self._create_card("Teacher", "El maestro"),
            self._create_card("Pencil", "El lápiz"),
        ]

        set_house = self._create_set(
            "Household Objects", "objects you would find in a house", household_cards
        )
        set_school = self._create_set(
            "School Vocabulary", "objects and concepts in a school", school_cards
        )

        resp_house = self.client.get(f"/practice/set/{set_house.id}")
        resp_school = self.client.get(f"/practice/set/{set_school.id}")


        self.assertEqual(resp_house.status_code, 200)
        self.assertEqual(len(resp_house.get_json()), len(household_cards))
        self.assertEqual(resp_school.status_code, 200)
        self.assertEqual(len(resp_school.get_json()), len(school_cards))

        # Ensure PracticeHistory entries were recorded
        self.assertEqual(
            PracticeHistory.query.filter_by(user_id=self.user.id).count(),
            len(household_cards) + len(school_cards),
        )

    def test_practice_without_set_returns_all_cards(self):
        for english, spanish in [("Dog", "El perro"), ("Cat", "El gato")]:
            self._create_card(english, spanish)

        resp = self.client.get("/practice/set")
        data = resp.get_json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(data), 2)

    def test_invalid_set_id(self):
        resp = self.client.get("/practice/set/99999")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("error", resp.get_json())


if __name__ == "__main__":
    unittest.main()
