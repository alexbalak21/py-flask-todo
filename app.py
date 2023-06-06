from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

app.config['SECRET_KEY'] = 'SuperSecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'

db = SQLAlchemy(app)


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
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

    def to_dict(self) -> dict:
        return {'id': self.id, 'text': self.text, 'complete': self.complete, 'user_id': self.user_id}


def message(content: str) -> str:
    return jsonify({'message': content})


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
        output.append(user.to_dict())
    return jsonify({'users': output})


@app.get('/user/<public_id>')
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return message('No user found.')
    return jsonify(user.to_dict())


@app.post('/user')
def create_user():
    data = request.get_json()
    hash_password = generate_password_hash(data['password'])
    new_user = User(public_id=str(uuid.uuid4()),
                    name=data['name'], password=hash_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return message('new user crated')


@app.put('/user/<public_id>')
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return message('No user found.')
    user.admin = True
    db.session.commit()
    return message('User has been promoted.')


@app.delete('/user/<public_id>')
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return message('No user found.')
    db.session.delete(user)
    db.session.commit()
    return message('The user has been deleted')


@app.post('/login')
def login():
    auth = request.