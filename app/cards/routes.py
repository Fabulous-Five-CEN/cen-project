from flask import jsonify, request, render_template
import requests
from . import cards_bp
from app import db
from app.models import Card, User
from datetime import datetime, timezone
import os

LECTO_API_URL = "https://lecto-translation.p.rapidapi.com/v1/translate/text"
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")  
LECTO_API_HOST = "lecto-translation.p.rapidapi.com"



@cards_bp.route("/")
def cards_home():
    return render_template("cards.html")

@cards_bp.route("/new", methods=["POST"])
def new_card():
    data = request.get_json() or {}

    # Mandatory Fields
    english_text = data.get('english_text')
    spanish_text = data.get('spanish_text')
    user_id = data.get('user_id')

    # Optional

    notes = data.get('notes')
    is_starred = data.get('is_starred', False)

    # check that mandatory fields are present 

    if not english_text or not spanish_text or not user_id:
        return jsonify({"error" : "Missing one of these required fields: english_text, spanish_text, user_id"}), 400


    # Check that user is in database

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404
    
    # add the card to db

    new_card = Card(
        english_text = english_text,
        spanish_text = spanish_text,
        notes=notes,
        is_starred=is_starred,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.session.add(new_card)
    db.session.commit()

    return jsonify ({
        "message" : "Card successfully created in database",
                "card": {
            "id": new_card.id,
            "english_text": new_card.english_text,
            "spanish_text": new_card.spanish_text,
            "notes": new_card.notes,
            "is_starred": new_card.is_starred,
            "user_id": new_card.user_id,
            "created_at": new_card.created_at.isoformat(),
        }
    }), 201


@cards_bp.route("/edit/<int:card_id>", methods = ["PUT"])
def edit_card(card_id):

    data = request.get_json() or {}

    card = db.session.get(Card, card_id)
    if not card:
            return jsonify({"Error" : f"No card exists in database with id {card_id}"}), 404
    

    english_text = data.get("english_text")
    spanish_text = data.get("spanish_text")
    notes = data.get("notes")
    is_starred = data.get("is_starred")

    if english_text is not None:
        card.english_text = english_text
    if spanish_text is not None:
        card.spanish_text = spanish_text
    if notes is not None:
        card.notes = notes
    if is_starred is not None:
        card.is_starred = is_starred

    card.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return jsonify({
            "message": "Card successfully updated",
            "card": {
                "id": card.id,
                "english_text": card.english_text,
                "spanish_text": card.spanish_text,
                "notes": card.notes,
                "is_starred": card.is_starred,
                "user_id": card.user_id,
                "updated_at": card.updated_at.isoformat(),
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update card: {str(e)}"}), 500
    

@cards_bp.route("/delete/<int:card_id>", methods = ["DELETE"])
def delete_card(card_id):
    card = db.session.get(Card, card_id)
    if not card:
        return jsonify({"error": f"No card found with id {card_id}"}), 404

    try:
        db.session.delete(card)
        db.session.commit()
        return jsonify({"message": f"Card with id {card_id} successfully deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete card: {str(e)}"}), 500



@cards_bp.route("/auto-translate", methods=["POST"]) 
def auto_translate():
    data = request.get_json() or {}
    text = data.get('text')
    direction = data.get('direction')

    if not text or direction not in ['english_to_spanish', 'spanish_to_english']:
            return jsonify({"error" : "Invalid request"}), 400
    

    #language direction

    if direction == 'english_to_spanish':
            src = 'en'
            target = 'es'

    else:
            src = 'es'
            target = 'en'

    payload = {
        "texts": [text],
        "to": [target],
        "from": src,
    }


    headers = {
        "content-type": "application/json",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": LECTO_API_HOST,
        "accept-encoding": "gzip"
    }

    # attempt api call

    try:
        response = requests.post(LECTO_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        translated_text = result["translations"][0]["translated"][0]

        return jsonify({
            "original_text": text,
            "from": src,
            "to": target,
            "translated_text": translated_text,
            "translated_characters": result.get("translated_characters")
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Translation request failed", "details": str(e)}), 500
