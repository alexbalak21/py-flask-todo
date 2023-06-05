from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

app.config['SECRET_KEY'] = 'SuperSecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


@app.get('/')
def home():
    return 'Home'


@app.get('/create')
def create():
    try:
        db.create_all()
        return 'Database Created'
    except:
        return 'Database Error'


@app.get('/user')
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)
    return jsonify({'users': output})


@app.get('/user/<user_id>')
def get_one_user():
    return ''


@app.post('/user')
def create_user():
    data = request.get_json()
    hash_password = generate_password_hash(data['password'])
    new_user = User(public_id=str(uuid.uuid4()),
                    name=data['name'], password=hash_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'new user crated'})


@app.put('/user/<user_id>')
def promote_user():
    return ''


@app.delete('/user/<user_id>')
def delete_user():
    return ''
