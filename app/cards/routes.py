from flask import jsonify, request
import requests
from . import cards_bp
from app import db
from app.models import Card, User
from datetime import datetime
import os

LECTO_API_URL = "https://lecto-translation.p.rapidapi.com/v1/translate/text"
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")  
LECTO_API_HOST = "lecto-translation.p.rapidapi.com"



@cards_bp.route("/")
def cards_home():
    return jsonify({"page": "Cards"})

@cards_bp.route("/new", methods=["POST"])
def new_card():
    data = request.get_json()

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

    user = User.query.get(user_id)
    if not user:
        return jsonify({"Error" : f"User with id {user_id} is not a registered user"}), 404
    
    # add the card to db

    new_card = Card(
        english_text = english_text,
        spanish_text = spanish_text,
        notes=notes,
        is_starred=is_starred,
        user_id=user_id,
        created_at=datetime.now(datetime.timezone.utc),
        updated_at=datetime.now(datetime.timezone.utc)
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

@cards_bp.route("/edit")
def edit_card():
    return jsonify({"page": "Edit Card"})

@cards_bp.route("/delete")
def delete_card():
    return jsonify({"page": "Delete Card"})



@cards_bp.route("/cards/auto-translate", methods=["POST"]) 
def auto_translate():
    data = request.get_json()
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