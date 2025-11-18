from flask import jsonify, request
from . import practice_bp
from app.extensions import db
from app.models.orm_objects import Card, User, SetTable, PracticeHistory
from datetime import datetime, timezone

@practice_bp.route("/")
def practice_home():
    return jsonify({"page": "Practice"})

@practice_bp.route("/", defaults={"set_id": None})
@practice_bp.route("/<int:set_id>")
def practice(set_id):
    """Gets set associated with the set_id and user_id"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id query parameter is required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
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
