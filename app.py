from flask import Flask, render_template, redirect, url_for, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus

app = Flask(__name__)



app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
modus = Modus(app)
db = SQLAlchemy(app)

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    email = db.Column(db.Text)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    def __init__(self, username, email, first_name, last_name):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

class Message(db.Model):

    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    important = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, important, user_id):
        self.important = important
        self.user_id = user_id


@app.route('/users', methods=["GET", "POST"])
def user_index():
    if request.method == "POST":
        db.session.add(User(
            request.form['username'],
            request.form['email'],
            request.form['first_name'],
            request.form['last_name']
        ))
        db.session.commit()
        return redirect(url_for('user_index'))
    return render_template('index.html', users=User.query.all())


@app.route('/users/new')
def user_new():
    return render_template('new.html')

@app.route('/users/<int:id>', methods=["GET", "PATCH", "DELETE"])
def user_show(id):
    if request.method == b"DELETE":
        db.session.delete(User.query.get(id))
        db.session.commit()
        return redirect(url_for('user_index'))

    if request.method == b"PATCH":
        user = User.query.get(id);
        user.username = request.form['username']
        user.email = request.form['email']
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_index'))
    return render_template('show.html', user=User.query.get(id))

@app.route('/users/<int:id>/edit')
def user_edit(id):
    return render_template('edit.html', user=User.query.get(id))

@app.route('/users/<int:id>/messages/new', methods=["GET"])
def message_new(id):
    return render_template("new_message.html", id=id)

@app.route('/users/<int:id>/messages', methods=["GET", "POST"])
def message_index(id):
    if request.method == "POST":
        # Save this message for the user id
        #redirect
        return redirect(url_for('message_index', id=id))
    return render_template('index_message.html', messages=User.query.get(id).messages.all())

@app.route('/users/<int:id>/messages/<int:message_id>', methods=["GET", "PATCH", "DELETE"])
def message_show(id, message_id):
    if request.method == b"DELETE":
        db.session.delete(Message.query.get(message_id))
        db.session.commit()
        return redirect(url_for('message_index', id=id))

    if request.method == b"PATCH":
        message = Message.query.get(message_id)
        message.important = request.form['important']
        message.message_id = id
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('message_index', id=id, message_id=message_id))

    return render_template('show_message.html', id=id, message_id=message_id, message=Message.query.get(message_id))


@app.route('/users/<int:id>/messages/<int:message_id>/edit')
def message_edit(id, message_id):
    return render_template('edit_message.html', id=id, message=Message.query.get(message_id))


if os.environ.get('env') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    debug = False
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/flask-sqlalchemy'
    debug = True



if __name__ == '__main__':
    app.run(debug=True)
