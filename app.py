from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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
    return ''


@app.get('/user/<user_id>')
def get_one_user():
    return ''


@app.post('/user')
def create_user():
    return ''


@app.put('/user/<user_id>')
def promote_user():
    return ''


@app.delete('/user/<user_id>')
def delete_user():
    return ''
