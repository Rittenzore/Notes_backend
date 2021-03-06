from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_BINDS'] = {'users': 'sqlite:///users.db',
                                  'notes': 'sqlite:///notes.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)
    name = db.Column(db.String)

    def __repr__(self):
        return '<User %r>' % self.id


class Note(db.Model):
    __bind_key__ = 'notes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, index=True)
    text = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    longitude = db.Column(db.String)
    latitude = db.Column(db.String)

    def __repr__(self):
        return '<Note %r>' % self.id


# FULL-WORKING SIGN-UP METHOD
@app.route('/sign-up', methods=['POST'])
def sign_up():
    username = str(request.form.get('username', None))
    password = str(request.form.get('password', None))
    email = str(request.form.get('email', None))
    name = str(request.form.get('name', None))
    user = User.query.filter_by(username=username).first()

    if name is None or email is None or name is None:
        return return_json(success=False,
                           error='fields are empty')

    if user:
        return return_json(success=False,
                           error="user already exists")

    new_user = User(username=username,
                    password=generate_password_hash(password, method='sha256'),
                    email=email,
                    name=name)
    db.session.add(new_user)
    db.session.commit()
    return return_json(success=True)


# FULL-WORKING SIGN-IN METHOD
@app.route('/sign-in', methods=['POST'])
def sign_in():
    username = str(request.form.get('username', None))
    password = str(request.form.get('password', None))
    if username is None or password is None:
        return return_json(success=False,
                           error='Fields are empty')

    user = User.query.filter_by(username=username).first()

    user_json = {
        "id": user.id,
        "username": user.username,
        "password": user.password,
        "name": user.name,
        "email": user.email
    }

    if not user or not check_password_hash(user.password, password):
        return return_json(success=False,
                           error='')

    return return_json(success=True,
                       data=user_json)


# FULL-WORKING GET-USER METHOD
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.filter_by(id=id).first()
    user_json = {
        "id": user.id,
        "username": user.username,
        "password": user.password,
        "name": user.name,
        "email": user.email
    }
    return return_json(success=True,
                       data=user_json)


# CREATE NOTE WORKING METHOD
@app.route('/create-note', methods=['POST'])
def create_note():
    if request.form.get("text", None) is None:
        return return_json(success=False,
                           error="Text is empty")

    text = str(request.form.get("text", None))
    user_id = int(request.form.get("user_id", None))
    longitude = str(request.form.get("longitude", None))
    latitude = str(request.form.get("latitude", None))
    note = Note(user_id=int(user_id),
                text=text,
                longitude=longitude,
                latitude=latitude)
    try:
        db.session.add(note)
        db.session.commit()
        print(note)
        return return_json(success=True)
    except:
        return return_json(success=False,
                           error='Database error')


# EDIT NOTE WORKING METHOD
@app.route('/edit-note/<int:note_id>', methods=['POST'])
def edit_note(note_id):
    if request.form.get("text", None) is None:
        return return_json(success=False,
                           error="Text is empty")

    new_text = str(request.form.get("text", None))
    longitude = str(request.form.get("longitude", None))
    latitude = str(request.form.get("latitude", None))
    note = Note.query.filter_by(id=note_id).first()
    note.text = new_text
    note.longitude = longitude
    note.latitude = latitude

    db.session.add(note)
    db.session.commit()
    return return_json(success=True)


@app.route('/remove-note', methods=['POST'])
def remove_note():
    id = int(request.form.get('id', None))
    note = Note.query.filter_by(id=id).first()

    try:
        db.session.delete(note)
        db.session.commit()
        return return_json(success=True)
    except:
        return return_json(success=False,
                           error='There was a problem deleting note.')


# GET NOTES WORKING METHOD
@app.route('/notes/<int:user_id>')
def get_notes(user_id):
    notes = Note.query.filter_by(user_id=user_id).all()
    notes_json = []
    for note in notes:
        note_model = Note(id=note.id,
                          user_id=user_id,
                          text=note.text,
                          date=note.date,
                          longitude=note.longitude,
                          latitude=note.latitude)
        note_json = {
            "id": note_model.id,
            "user_id": note_model.user_id,
            "text": note_model.text,
            "date": note_model.date,
            "longitude": note_model.longitude,
            "latitude": note_model.latitude
        }
        notes_json.append(note_json)
    return return_json(success=True,
                       data={'notes': notes_json})


@app.route('/note/<int:user_id>/<int:id>', methods=['GET'])
def get_note(id, user_id):
    note = Note.query.filter_by(id=id, user_id=user_id).first()

    note_json = {
        "id": note.id,
        "user_id": note.user_id,
        "text": note.text,
        "date": note.date,
        "longitude": note.longitude,
        "latitude": note.latitude
    }
    print(note_json)

    return return_json(success=True,
                       data=note_json)


def return_json(success: bool, data: dict = None, error=None):
    return jsonify(
        {
            'success': success,
            'data': data,
            'error': error
        }
    )


# TO RUN WRITE "flask run -h localhost -p 8000" IN CONSOLE
if __name__ == "__main__":
    app.run(debug=True)
