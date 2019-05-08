from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tinydb import TinyDB
from tinydb import Query
import hashlib
from recognizer import Recognizer

app = Flask(__name__)
# Limiting the requests to avoid DOS attack
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

db = TinyDB('users.json')
recognizer = Recognizer()
""""""
"""Connecting Area"""
""""""


@app.route('/connect/<string:username>/<string:password>/<string:image>')
@limiter.limit("10 per hour")
def connect(username, password, image):
    global recognizer
    # Connect Process
    data = get_user_data(username)
    if len(data) != 0:
        return jsonify({'error': 'Something went wrong'})
    user_data = data[0]
    if user_data['username'] == username and user_data['password'] == string_to_md5(password):
        eye_distance, avarage_color = recognizer.get_data(image)
        distance_percentage = (100 * min(eye_distance, user_data['eyes_dis'])) / max(eye_distance,
                                                                                     user_data['eyes_dis'])
        color_percentage = (100 * min(avarage_color, user_data['avg_color'])) / max(avarage_color,
                                                                                    user_data['avg_color'])
        return jsonify({'success': (distance_percentage+color_percentage)/2})
    return jsonify({'error': 'username or password is invalid'})


@app.route('/connect/<string:username>/<string:password>')
@limiter.limit("3 per hour")
def connect_no_image(username, password):
    return jsonify({'error': 'forgot image'})


@app.route('/connect/<string:username>')
@limiter.limit("3 per hour")
def connect_no_password(username):
    return jsonify({'error1': 'forgot password', 'error2': 'forgot image'})


""""""
"""Registering Area"""
""""""


@app.route('/register/<string:username>/<string:password>/<string:image>')
@limiter.limit("10 per hour")
def register(username, password, image):
    global recognizer
    if valid_username(username):
        eye_distance, avarage_color = recognizer.get_data(image)
        return register_to_db(username, password, eye_distance, avarage_color)
    return jsonify({'error': 'invalid username'})


@app.route('/register/<string:username>/<string:password>')
@limiter.limit("3 per hour")
def register_no_image(username, password):
    return jsonify({'error': 'forgot image'})


@app.route('/register/<string:username>')
@limiter.limit("3 per hour")
def register_no_password(username):
    return jsonify({'error1': 'forgot password', 'error2': 'forgot image'})


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@limiter.limit("3 per hour")
def catch_all(path):
    return jsonify({"error": "Not Found"})


def valid_username(username):
    global db
    User = Query()
    return len(db.search(User.username == username)) == 0


def register_to_db(username, password, eyes_distance, avarage_color):
    global db
    db.insert({"username": username, "password": string_to_md5(password), "eyes_dis": eyes_distance,
               'avg_color': avarage_color})
    return {"username": username, "password": password, "eyes_dis": eyes_distance, 'avg_color': avarage_color}


def get_user_data(username):
    global db
    User = Query()
    return db.search(User.username == username)


def string_to_md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


if __name__ == '__main__':
    print(get_user_data('shahar'))
    app.run(debug=True)
