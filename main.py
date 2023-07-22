from flask import Flask, request, jsonify, abort, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from waitress import serve
from functools import wraps
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Your secret API key
API_KEY = os.environ.get("API_KEY")

class User(db.Model):
    discord_id = db.Column(db.String(), primary_key=True)
    credits = db.Column(db.Integer, default=3)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('Authorization') and request.headers.get('Authorization') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/user', methods=['GET'])
@require_api_key
def get_users():
    users = User.query.all()
    return users_schema.jsonify(users)

@app.route('/api/user/<discord_id>', methods=['GET'])
@require_api_key
def get_user(discord_id):
    user = User.query.get(discord_id)
    if user is None:
        user = User(discord_id=discord_id, credits=3)
        db.session.add(user)
        db.session.commit()
    return user_schema.jsonify(user)

@app.route('/api/user/<discord_id>', methods=['PUT'])
@require_api_key
def update_user(discord_id):
    user = User.query.get(discord_id)
    if user is None:
        abort(404)
    user.credits += request.json.get('credits', 0)
    db.session.commit()
    return user_schema.jsonify(user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    serve(app, host="0.0.0.0", port=0)
