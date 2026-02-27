from flask import jsonify, request, render_template
from flask_login import current_user, login_required
import requests
from sqlalchemy import or_
from . import cards_bp
from app import db
from app.models import Card, User
from datetime import datetime, timezone
import os


# Auto Translate API Setup 

LECTO_API_URL = "https://lecto-translation.p.rapidapi.com/v1/translate/text"
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")  
LECTO_API_HOST = "lecto-translation.p.rapidapi.com"


# Default home route
@cards_bp.route("/")
@login_required
def cards_home():
    user_id = current_user.id

    # Retrieve each card
    cards = (
        db.session.query(Card)
        .filter(or_(Card.user_id == user_id, Card.user_id.is_(None)))
        .order_by(Card.id)        
        .all()
    )

    cards_data = []
    for card in cards:
        # Retrieve current set membership for each card
        sets_info = [{"id": s.id, "name": s.name} for s in card.sets]

        cards_data.append({
            "id": card.id,
            "english_text": card.english_text,
            "spanish_text": card.spanish_text,
            "notes": card.notes,
            "is_starred": card.is_starred,
            "created_at": card.created_at.isoformat(),
            "updated_at": card.updated_at.isoformat(),
            "sets": [s["name"] for s in sets_info],    
            "set_ids": [s["id"] for s in sets_info]    
        })

    return render_template("cards.html", cards=cards_data)


         
# Create new card route
@cards_bp.route("/new", methods=["POST"])
@login_required
def new_card():
    data = request.get_json() or {}

    # Mandatory Fields
    english_text = data.get('english_text')
    spanish_text = data.get('spanish_text')
    user_id = current_user.id

    # Optional

    notes = data.get('notes')
    is_starred = data.get('is_starred', False)

    # check that mandatory fields are present 
    if not english_text or not spanish_text:
        return jsonify({"error" : "Missing one of these required fields: english_text, spanish_text"}), 400


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

# Edit card fields
@cards_bp.route("/edit/<int:card_id>", methods = ["PUT"])
@login_required
def edit_card(card_id):

    # Confirm active user is valid
    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404
    

    # Confirm card is valid and exists
    data = request.get_json() or {}
    card = db.session.get(Card, card_id)
    if not card:
            return jsonify({"Error" : f"No card exists in database with id {card_id}"}), 404
    

    # Obtain data
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
    
# Delete card route
@cards_bp.route("/delete/<int:card_id>", methods = ["DELETE"])
@login_required
def delete_card(card_id):

    # Confirm valid user in database
    user_id = current_user.id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404
    
    # Confirm valid card in database
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


# Auto Translate route
@cards_bp.route("/auto-translate", methods=["POST"]) 
@login_required
def auto_translate():
    # retireve data fields
    data = request.get_json() or {}
    text = data.get('text')
    direction = data.get('direction')
    user_id = current_user.id

    # Confirm valid user in database
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404

    # Check that valid language direction is present in JSON
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
