from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
app = Flask(__name__)

app.config['SECRET_KEY'] = 'SuperSecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'

db = SQLAlchemy(app)

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwdWJsaWNfaWQiOiIyYjc3MTQwMS0xNjIyLTQ1YWYtOGY0ZC05M2IxNGEwMjVjNzUiLCJleHAiOjE2ODYwODc4MDN9.7GOQVJJRNVdXqaHxvhalxr6iYk3QykQKuyg1hSRuEZ4"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return message('Token is missing'), 401
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return message('token is invalid'), 401
        return f(current_user, *args, **kwargs)
    return decorated


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

    def to_dict(self) -> dict:
        return {'id': self.id, 'public_id': self.public_id, 'name': self.name, 'password': self.password, 'admin': self.admin}


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255))
    complete = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer)

    def to_dict(self) -> dict:
        return {'id': self.id, 'text': self.text, 'complete': self.complete, 'user_id': self.user_id}


def message(content: str) -> str:
    return jsonify({'message': content})


@app.get('/')
def home():
    return 'Home', 201


@app.get('/create')
def create():
    try:
        db.create_all()
        return 'Database Created'
    except:
        return 'Database Error'


# GET ALL USERS
@app.get('/user')
@token_required
def get_all_users(current_user):
    users = User.query.all()
    output = []
    for user in users:
        output.append(user.to_dict())
    return jsonify({'current user': current_user.to_dict(), 'users': output})


# GET 1 USER
@app.get('/user/<public_id>')
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return message('No user found.')
    return jsonify(user.to_dict())


# CREATE USE
@app.post('/user')
def create_user():
    data = request.get_json()
    hash_password = generate_password_hash(data['password'])
    new_user = User(public_id=str(uuid.uuid4()),
                    name=data['name'], password=hash_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return message('new user crated'), 201


# PROMOTE USER
@app.put('/user/<public_id>')
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return message('No user found.')
    user.admin = True
    db.session.commit()
    return message('User has been promoted.'), 202


# DELETE USER
@app.delete('/user/')
@token_required
def delete_user(current_user):
    user = User.query.filter_by(public_id=current_user.public_id).first()
    if not user:
        return message('No user found.')
    db.session.delete(user)
    db.session.commit()
    return message('The user has been deleted'), 202


# LOGIN
@app.post('/login')
def login():
    data = request.get_json()
    if not data['name'] or not data['password']:
        return message('Fields missing in request')
    user = User.query.filter_by(name=data['name']).first()
    if not user:
        return message('User not found')
    if check_password_hash(user.password, data['password']):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token}), 202
    return message('Password incorrect'), 401


# POST todo
@app.post('/todo')
@token_required
def create_todo(current_user):
    data = request.get_json()
    if not data['text']:
        return message('Bad data submited')
    new_todo = Todo(text=data['text'], user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    return message('Todo created'), 201


@app.get('/todo')
@token_required
def get_all_todos(current_user):
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    output = []
    for todo in todos:
        output.append(todo.to_dict())
    return jsonify(output)


@app.delete('/todo/<id>')
@token_required
def delete_todo(current_user, id):
    todo = Todo.query.filter_by(user_id=current_user.id, id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return message('Todo deleted'), 202
