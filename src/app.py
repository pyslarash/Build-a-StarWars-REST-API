"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, make_response
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Favorites, Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Getting a list of all the users in the database
@app.route('/user', methods=['GET'])
def user_get():

    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))

    return jsonify(all_users), 200

# Getting information about a single User:
@app.route('/user/<int:user_id>', methods=['GET'])
def get_single_user(user_id):

    user = User.query.get(user_id)
    if user is None:
        response = make_response(jsonify({'message': 'User not found'}), 404)
        response.headers['Content-Type'] = 'application/json'
        return response

    serialized_char = user.serialize()
    return jsonify(serialized_char), 200

# Creating a new user
@app.route('/user', methods=['POST'])
def user_post():

    request_body_user = request.get_json()
    user_add = User(email=request_body_user["email"], password=request_body_user["password"])
    db.session.add(user_add)
    db.session.commit()
    print(request_body_user)
    return jsonify(request_body_user), 200

# Updating a user with a certain ID
@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):

    request_body_user = request.get_json()

    user = User.query.get(user_id)
    if user is None:
        raise APIException('User not found', status_code=404)

    if "email" in request_body_user:
        user.email = request_body_user["email"]
    if "password" in request_body_user:
        user.password = request_body_user["password"]
    if "is_active" in request_body_user:
        user.is_active = request_body_user["is_active"]
    if "favorites" in request_body_user:
        user.favorites = request_body_user["favorites"]
    db.session.commit()

    return jsonify(request_body_user), 200 

# Deleting a user with a certain ID
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):

     # delete associated favorites
    Favorites.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # delete user
    user = User.query.get(user_id)
    if user is None:
        raise APIException('User not found', status_code=404)

    db.session.delete(user)
    db.session.commit()

    return jsonify("User deleted"), 200

# Getting a list of all the Characters in the database
@app.route('/characters', methods=['GET'])
def characters_get():

    characters = Characters.query.all()
    all_characters = list(map(lambda x: x.serialize(), characters))

    return jsonify(all_characters), 200

# Getting information about a single Character:
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_single_character(character_id):

    char = Characters.query.get(character_id)
    if char is None:
        response = make_response(jsonify({'message': 'Character not found'}), 404)
        response.headers['Content-Type'] = 'application/json'
        return response

    serialized_char = char.serialize()
    return jsonify(serialized_char), 200


# Creating a new Character

@app.route('/characters', methods=['POST'])
def char_post():

    request_body_char = request.get_json()
    char = Characters(character_name=request_body_char["character_name"], height=request_body_char["height"], weight=request_body_char["weight"], birth_year=request_body_char["birth_year"], skin_color=request_body_char["skin_color"], eye_color=request_body_char["eye_color"], hair_color=request_body_char["hair_color"])
    db.session.add(char)
    db.session.commit()
    print(request_body_char)
    return jsonify(request_body_char), 200

# Getting a list of all the Planets in the database
@app.route('/planets', methods=['GET'])
def planets_get():

    planets = Planets.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets))

    return jsonify(all_planets), 200

# Getting information about a single Planet:
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):

    planet = Planets.query.get(planet_id)
    if planet is None:
        response = make_response(jsonify({'message': 'Planet not found'}), 404)
        response.headers['Content-Type'] = 'application/json'
        return response

    serialized_planet = planet.serialize()
    return jsonify(serialized_planet), 200

# Creating a new Planet
@app.route('/planets', methods=['POST'])
def planet_post():

    request_body_planet = request.get_json()
    planet = Planets(planet_name=request_body_planet["planet_name"], rotation_period=request_body_planet["rotation_period"], orbital_period=request_body_planet["orbital_period"], gravity=request_body_planet["gravity"], terrain=request_body_planet["terrain"])
    db.session.add(planet)
    db.session.commit()
    print(request_body_planet)
    return jsonify(request_body_planet), 200

# Add a new favorite planet to the current user with the planet id = planet_id
@app.route('/user/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    if not user:
        raise APIException('User not found', status_code=404)

    planet = Planets.query.get(planet_id)
    if not planet:
        raise APIException('Planet not found', status_code=404)

    # Check if the planet has already been added as a favorite for the user
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        return jsonify({'message': f'{planet.planet_name} is already a favorite'}), 400

    favorite = Favorites(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({'message': f'{planet.planet_name} added as a favorite for user {user_id}'}), 201


@app.route('/user/<int:user_id>/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(user_id, character_id):
    user = User.query.get(user_id)
    if not user:
        raise APIException('User not found', status_code=404)

    character = Characters.query.get(character_id)
    if not character:
        raise APIException('Character not found', status_code=404)

    # Check if the character has already been added as a favorite for the user
    favorite = Favorites.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite:
        return jsonify({'message': f'{character.character_name} is already a favorite'}), 400

    favorite = Favorites(user_id=user_id, character_id=character_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({'message': f'{character.character_name} added to favorites'}), 200

# Get the favorites for a user
@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        raise APIException('User not found', status_code=404)

    favorites = []
    for favorite in user.favorites:
        if favorite.planet_id:
            planet = Planets.query.get(favorite.planet_id)
            favorites.append({'planet_id': planet.id, 'planet_name': planet.planet_name})
        elif favorite.character_id:
            character = Characters.query.get(favorite.character_id)
            favorites.append({'character_id': character.id, 'character_name': character.character_name})

    return jsonify({'favorites': favorites}), 200

# Deleting a character with a certain ID
@app.route('/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):

     # delete associated favorites
    Favorites.query.filter_by(character_id=character_id).delete()
    db.session.commit()

    # delete character
    character = Characters.query.get(character_id)
    if character is None:
        raise APIException('Character not found', status_code=404)

    db.session.delete(character)
    db.session.commit()

    return jsonify("Character deleted"), 200

# Deleting a planet with a certain ID
@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):

     # delete associated favorites
    Favorites.query.filter_by(planet_id=planet_id).delete()
    db.session.commit()

    # delete planet
    planet = Planets.query.get(planet_id)
    if planet is None:
        raise APIException('Planet not found', status_code=404)

    db.session.delete(planet)
    db.session.commit()

    return jsonify("Planet deleted"), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
