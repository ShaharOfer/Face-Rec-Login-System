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
    default_limits=["400 per day", "500 per hour"]
)

db = TinyDB('users.json')
recognizer = Recognizer()


@app.route('/', methods=['GET', 'POST'])
def index():
    with open('login.html', 'r') as file:
        return file.read()


@app.route('/login', methods=['GET', 'POST'])
def login():
    with open('login.html', 'r') as file:
        return file.read()


@app.route('/register', methods=['GET', 'POST'])
def register_regular():
    with open('register.html', 'r') as file:
        return file.read()


@app.route('/webcam.min.js', methods=['GET', 'POST'])
def webcam_min_js():
    with open('webcam.min.js', 'r') as file:
        return file.read()


"""
Connecting Area
"""


@app.route('/connect/<string:username>/<string:password>/<string:image>', methods=['GET', 'POST'])
@limiter.limit("100 per hour")
def connect(username, password, image):
    global recognizer
    # Connect Process
    data = get_user_data(username)
    if len(data) != 1:
        return jsonify({'error': 'Something went wrong'})
    user_data = data[0]
    if user_data['username'] == username and user_data['password'].lower() == string_to_md5(password).lower():
        if recognizer.validity_check(image):
            eye_distance, avarage_color = recognizer.get_data(image)
            distance_percentage = (100 * min(eye_distance, user_data['eyes_dis'])) / max(eye_distance,
                                                                                         user_data['eyes_dis'])
            color_percentage = (100 * min(avarage_color, user_data['avg_color'])) / max(avarage_color,
                                                                                        user_data['avg_color'])
            return jsonify({'success': (distance_percentage + color_percentage) / 2})
    return jsonify({'error': 'username, password or image is invalid'})


@app.route('/connect/<string:username>/<string:password>', methods=['GET', 'POST'])
@limiter.limit("300 per hour")
def connect_no_image(username, password):
    return jsonify({'error': 'forgot image'})


@app.route('/connect/<string:username>', methods=['GET', 'POST'])
@limiter.limit("200 per hour")
def connect_no_password(username):
    return jsonify({'error1': 'forgot password', 'error2': 'forgot image'})


""""""
"""Registering Area"""
""""""


@app.route('/register/<string:username>/<string:password>/<string:image>', methods=['GET', 'POST'])
@limiter.limit("100 per hour")
def register(username, password, image):
    global recognizer
    if valid_username(username):
        if valid_password(password):
            if recognizer.validity_check(image):
                eye_distance, avarage_color = recognizer.get_data(image)
                register_to_db(username, password, eye_distance, avarage_color)
                return jsonify(
                    {"username": username, "password": password, "eyes_dis": eye_distance, 'avg_color': avarage_color})
            else:
                return jsonify({'error': 'invalid image'})
        else:
            return jsonify({'error': 'invalid password'})
    else:
        return jsonify({'error': 'invalid username'})


@app.route('/register/<string:username>/<string:password>', methods=['GET', 'POST'])
@limiter.limit("300 per hour")
def register_no_image(username, password):
    return jsonify({'error': 'forgot image'})


@app.route('/register/<string:username>', methods=['GET', 'POST'])
@limiter.limit("300 per hour")
def register_no_password(username):
    return jsonify({'error1': 'forgot password', 'error2': 'forgot image'})


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
@limiter.limit("300 per hour")
def catch_all(path):
    return jsonify({"error": "Not Found"})


def valid_password(password):
    """Checking if the password exists in the database"""
    global db
    User = Query()
    return len(db.search(User.password == string_to_md5(password))) == 0


def valid_username(username):
    """Checking if the username exists in the database"""
    global db
    User = Query()
    return len(db.search(User.username == username)) == 0


def register_to_db(username, password, eyes_distance, avarage_color):
    """Receiving the information and inserting it into the database"""
    global db
    db.insert({"username": username, "password": string_to_md5(password), "eyes_dis": eyes_distance,
               'avg_color': avarage_color})


def get_user_data(username):
    """Receiving the username
    returning the information about the username"""
    global db
    User = Query()
    return db.search(User.username == username)


def string_to_md5(string):
    """Simply converting string into md5 for information security purposes"""
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


if __name__ == '__main__':
    app.run(debug=True)
