import logging
import os
import time
from typing import Tuple, Union

from flask import Flask, jsonify, render_template, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from waitress import serve
from werkzeug.wrappers import Response

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

logging.basicConfig(filename='transaction.log', level=logging.INFO)

class User(db.Model):
  id = db.Column(db.String(100), primary_key=True)
  credits = db.Column(db.Integer, default=3)
  last_transaction = db.Column(db.Integer, default=int(time.time()))

  def __repr__(self):
    return f"User('{self.id}', '{self.credits}', '{self.last_transaction}')"


class UserSchema(ma.SQLAlchemyAutoSchema):

  class Meta:
    model = User


user_schema = UserSchema()
users_schema = UserSchema(many=True)

API_KEY = os.environ.get('API_KEY')

rate_limit_data = {}
MAX_REQUESTS_PER_SECOND = 1
MAX_REQUESTS_PER_30_SECONDS = 3

@app.before_request
def rate_limit():
  now = time.time()
  ip = request.remote_addr
  hist = rate_limit_data.get(ip, [])
  
  hist = [t for t in hist if now - t < 30]
  
  if len(hist) >= MAX_REQUESTS_PER_30_SECONDS or (len(hist) >= 1 and now - hist[-1] < 1):
    return jsonify({'error': 'Too many requests'}), 429

  hist.append(now)
  rate_limit_data[ip] = hist


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/user/<id>', methods=['GET', 'PUT'])
def get_user(id: str) -> Union[Response, Tuple[Response, int]]:
    user = User.query.get(id)
    if request.method == 'GET':
        if not user:
            user = User(id=id)
            db.session.add(user)
            db.session.commit()
        return user_schema.jsonify(user)
    elif request.method == 'PUT':
        key = request.headers.get('Authorization')
        if key and key == API_KEY:
            value = 0
            if request.json:
                value = request.json.get('value', 0)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            elif user.credits + value < 0:
                return jsonify({'error': 'Insufficient credits'}), 402
            else:
                user.credits += value
                user.last_transaction = int(time.time())
                db.session.commit()
                return user_schema.jsonify(user)
        else:
            return jsonify({'error': 'Unauthorized'}), 401
    else:
        return jsonify({'error': 'Method not allowed'}), 405



@app.before_request
def log_request_info():
  logging.info('Headers: %s', request.headers)
  logging.info('Body: %s', request.get_data())


if __name__ == '__main__':
  with app.app_context():
    db.create_all()
  host = os.environ.get("FLASK_HOST") or "0.0.0.0"
  port = os.environ.get("FLASK_PORT") or 0
  serve(app, host=host, port=port)
