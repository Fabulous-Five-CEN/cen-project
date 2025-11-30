import os
import sys
import unittest

from sqlalchemy.exc import SQLAlchemyError

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db
from app.models import Card, User

SEED_USER_EMAIL = os.environ.get("SEED_EMAIL", "amanda@test.com")

test_cards = [
    {
        "spanish_text": "Hola",
        "english_text": "Hello",
        "notes": "A common greeting.",
    },
    {
        "spanish_text": "Gracias",
        "english_text": "Thank you",
    },
    {
        "spanish_text": "¿Cómo estás?",
        "english_text": "How are you?",
    },
]


class SeedCardsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def test_seed_cards(self):
        try:
            user = User.query.filter_by(email=SEED_USER_EMAIL).first()
            self.assertIsNotNone(
                user,
                f"Could not find the user '{SEED_USER_EMAIL}'. Please seed users first.",
            )

            created = 0
            for card_data in test_cards:
                card_exists = Card.query.filter_by(
                    user_id=user.id, spanish_text=card_data["spanish_text"]
                ).first()

                if not card_exists:
                    new_card = Card(
                        spanish_text=card_data["spanish_text"],
                        english_text=card_data["english_text"],
                        notes=card_data.get("notes", ""),
                        user_id=user.id,
                    )
                    db.session.add(new_card)
                    created += 1

            db.session.commit()
            total_cards = Card.query.filter_by(user_id=user.id).count()
            self.assertGreaterEqual(
                total_cards, len(test_cards), "Not all test cards were created"
            )
            print(f"Seeded {created} cards for user {SEED_USER_EMAIL}.")
        except SQLAlchemyError as e:
            db.session.rollback()
            self.fail(f"An error occurred while seeding cards: {e}")


if __name__ == "__main__":
    unittest.main()
