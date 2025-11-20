from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    cards = db.relationship(
        "Card",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    sets = db.relationship(
        "SetTable",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    practice_entries = db.relationship(
        "PracticeHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, candidate: str) -> bool:
        if not candidate:
            return False
        return check_password_hash(self.password_hash, candidate)


class Card(db.Model):
    __tablename__ = "Card"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spanish_text = db.Column(db.Text, nullable=False)
    english_text = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    is_starred = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("User.id", ondelete="CASCADE"), nullable=True
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = db.relationship(
        "User",
        back_populates="cards",
        passive_deletes=True,
    )
    sets = db.relationship(
        "SetTable",
        secondary="CardSet",
        back_populates="cards",
    )
    practice_entries = db.relationship(
        "PracticeHistory",
        back_populates="card",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SetTable(db.Model):
    __tablename__ = "SetTable"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(
        db.Integer, db.ForeignKey("User.id", ondelete="CASCADE"), nullable=True
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = db.relationship(
        "User",
        back_populates="sets",
        passive_deletes=True,
    )
    cards = db.relationship(
        "Card",
        secondary="CardSet",
        back_populates="sets",
    )
    practice_entries = db.relationship(
        "PracticeHistory",
        back_populates="set",
        passive_deletes=True,
    )


class CardSet(db.Model):
    __tablename__ = "CardSet"

    card_id = db.Column(
        db.Integer,
        db.ForeignKey("Card.id", ondelete="CASCADE"),
        primary_key=True,
    )
    set_id = db.Column(
        db.Integer,
        db.ForeignKey("SetTable.id", ondelete="CASCADE"),
        primary_key=True,
    )


class PracticeHistory(db.Model):
    __tablename__ = "PracticeHistory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("User.id", ondelete="CASCADE"),
        nullable=True,
    )
    card_id = db.Column(
        db.Integer,
        db.ForeignKey("Card.id", ondelete="CASCADE"),
        nullable=True,
    )
    set_id = db.Column(
        db.Integer,
        db.ForeignKey("SetTable.id", ondelete="SET NULL"),
        nullable=True,
    )
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="practice_entries", passive_deletes=True)
    card = db.relationship("Card", back_populates="practice_entries", passive_deletes=True)
    set = db.relationship("SetTable", back_populates="practice_entries", passive_deletes=True)
