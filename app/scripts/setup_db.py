import sys
import os
from sqlalchemy.exc import SQLAlchemyError

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from app import create_app, db


from app.models import User, Card, SetTable, CardSet, PracticeHistory


app = create_app()

def setup_database():
    """
    Connects to the database configured in docker-compose
    and creates all tables based on the models defined in the application.
    This is the standard Flask-SQLAlchemy way.
    """
    # The app_context makes sure the application is properly configured
    with app.app_context():
        try:
            print("Connecting to the database and creating tables if they don't exist...")

            # This single command looks at all the models that were imported
            # and creates the corresponding tables in the MariaDB database.

            db.create_all()

            print("\nDatabase setup complete. All tables are ready.")

        except SQLAlchemyError as e:
            print(f"An error occurred during database setup: {e}")
  

if __name__ == '__main__':
    setup_database()