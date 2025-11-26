from flask import jsonify, request, render_template
from . import practice_bp
from app.extensions import db
from app.models.orm_objects import Card, User, SetTable, PracticeHistory
from datetime import datetime, timezone
from flask_login import login_user, logout_user, login_required, current_user



def serialize_set(set_obj):
    """Converts a SetTable object into a JSON-friendly dictionary."""
    return {
        "id": set_obj.id,
        "name": set_obj.name,
        "description": set_obj.description,
        "user_id": set_obj.user_id,
        "card_count": len(set_obj.cards),
        "created_at": set_obj.created_at.isoformat(),
        "updated_at": set_obj.updated_at.isoformat()
    }


@login_required
@practice_bp.route("/")
def practice_home():
    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404

    all_sets = SetTable.query.filter_by(user_id=user_id).all()
    sets = [serialize_set(s) for s in all_sets]
    return render_template("practice.html", sets=sets)  

@login_required
@practice_bp.route("/set", defaults={"set_id": None})
@practice_bp.route("/set/<int:set_id>")
def practice(set_id):
    """Gets set associated with the set_id and user_id"""
    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404
    
    # check that set_id is a valid set belonging to the user via user_id
        # retrieve all cards associated with that set

    if set_id is not None:
        set_obj = SetTable.query.filter_by(id=set_id, user_id=user.id).first()
        if not set_obj:
            return jsonify({"error": f"Set {set_id} not found or does not belong to this user_id"}), 404
        cards = set_obj.cards
    
    else:
    # or if set_id is blank (no json was retrieved, so no set was selected, we assume the user wants to do ALL their cards)
        # retrieve all cards associated with the user
        cards = Card.query.filter_by(user_id=user.id).all()

    # create dict object returning all card information to the frontend via json

    cards_dict = [
        {
            "id": card.id,
            "spanish_text": card.spanish_text,
            "english_text": card.english_text,
            "notes": card.notes,
            "is_starred": card.is_starred,
            "set_ids": [s.id for s in card.sets],
        }
        for card in cards
    ]

    # update practiceHistory
    practiceHistory(cards, user.id, set_id)


    return jsonify(cards_dict), 200

# a function that marks all the cards as practiced in the PracticeHistory table
def practiceHistory(cards, user_id, set_id=None):
    # go into db and create practicehistory object for each card in the cards_dict
    timestamp = datetime.now(timezone.utc)
    for card in cards:
        history_entry = PracticeHistory(
            user_id=user_id,
            card_id=card.id,
            set_id=set_id,
            timestamp=timestamp
        )
        db.session.add(history_entry)
    db.session.commit()
