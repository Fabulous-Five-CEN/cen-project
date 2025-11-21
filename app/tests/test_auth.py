import unittest

from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User


class AuthRouteTests(unittest.TestCase):
    def setUp(self):
        config_override = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False},
            },
            "WTF_CSRF_ENABLED": False,
        }
        self.app = create_app(config_override)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.password = "Password123!"
        self.user = User(
            email="login@test.com",
            password_hash=generate_password_hash(self.password),
            display_name="Login Tester",
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_success(self):
        with self.client as client:
            resp = client.post(
                "/auth/login",
                json={"email": self.user.email, "password": self.password},
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["user"]["email"], self.user.email)

            with client.session_transaction() as sess:
                self.assertEqual(sess.get("_user_id"), str(self.user.id))

    def test_login_requires_credentials(self):
        resp = self.client.post("/auth/login", json={"email": self.user.email})
        self.assertEqual(resp.status_code, 400)

    def test_login_rejects_bad_password(self):
        resp = self.client.post(
            "/auth/login", json={"email": self.user.email, "password": "wrong"}
        )
        self.assertEqual(resp.status_code, 401)

    def test_logout_clears_session(self):
        with self.client as client:
            client.post(
                "/auth/login",
                json={"email": self.user.email, "password": self.password},
            )
            resp = client.post("/auth/logout")
            self.assertEqual(resp.status_code, 200)
            with client.session_transaction() as sess:
                self.assertIsNone(sess.get("_user_id"))


if __name__ == "__main__":
    unittest.main()
