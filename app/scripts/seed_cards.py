import sys
import os
from sqlalchemy.exc import SQLAlchemyError

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import what we need
from app import create_app, db
from app.models import Card, User # Make sure to import your Card and User models

# --- Define your test card data here ---
test_cards = [
    {
        "spanish_text": "Hola",
        "english_text": "Hello",
        "notes": "A common greeting."
    },
    {
        "spanish_text": "Gracias",
        "english_text": "Thank you",
    },
    {
        "spanish_text": "¿Cómo estás?",
        "english_text": "How are you?",
    }
]

def seed_cards():
    app = create_app()
    with app.app_context():
        try:
            # Find a user to assign the cards to. We'll use one of the seeded users.
            amanda = User.query.filter_by(email="amanda@test.com").first()

            if not amanda:
                print("Could not find the user 'amanda@test.com' to assign cards to. Please seed users first.")
                return

            print(f"Found user: {amanda.display_name}. Seeding cards for this user...")

            for card_data in test_cards:
                # Check if a card with the same text already exists for this user
                card_exists = Card.query.filter_by(
                    user_id=amanda.id,
                    spanish_text=card_data["spanish_text"]
                ).first()

                if not card_exists:
                    new_card = Card(
                        spanish_text=card_data["spanish_text"],
                        english_text=card_data["english_text"],
                        notes=card_data.get("notes", ""), # Use .get for optional fields
                        user_id=amanda.id
                    )
                    db.session.add(new_card)

            db.session.commit()
            print("Test cards seeded successfully!")

        except SQLAlchemyError as e:
            print(f"An error occurred while seeding cards: {e}")
            db.session.rollback()

if __name__ == "__main__":
    seed_cards()