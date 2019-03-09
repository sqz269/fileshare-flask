from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import Flask

def db_mgmt_init():
    global db
    global bcrypt
    db_uri = input("Enter database uri: ")
    app = Flask(__name__)
    db = SQLAlchemy(app)
    bcrypt = Bcrypt(app=app)
    print("CONNECTING TO DATABASE")
    app.config.update({"SQLALCHEMY_DATABASE_URI": db_uri})
    tables = db.engine.table_names()
    if not tables:
        print("NO TABLES DETECTED IN THE DATABASE.")
        input("PRESS ENTER TO EXIT")
        raise SystemExit(0)


def db_mgmt_ask_option():
    option = int(input("Select Option By Number:\n0)List All Users\n1)Add User\n2)Delete User (Key)\n3)Delete User (Username)\n"))
    return option


def list_all_users():
    users = User.query.all()
    for user in users:
        print(user)


def add_user_wrapper():
    while True:
        try:
            username = input("Username: ")
            password = input("Password: ")
            database_add_user(username, password)
            db.session.commit()
            new_usr = input("User {} has been added to the database\nAdd another one (y/n)?".format(username))
            if new_usr.lower() == "y":
                continue
            else:
                break
        except BrokenPipeError as e:
            print("Failed to add new user. Exception occurred: {}".format(e))
            break


def delete_user_wrapper_by_name():
    while True:
        try:
            username = input("Username: ")
            database_delete_user_by_username(username)
            db.session.commit()
            new_usr = input("User {} has been deleted\nDelete another one (y/n)?".format(username))
            if new_usr.lower() == "y":
                continue
            else:
                break
        except Exception as e:
            print("Failed to delete user. Exception occurred: {}".format(e))
            break

def delete_user_wrapper_by_name():
    while True:
        try:
            key = input("ID: ")
            database_delete_user_by_primary_key(key)
            db.session.commit()
            new_usr = input("User {} has been deleted\nDelete another one (y/n)?".format(username))
            if new_usr.lower() == "y":
                continue
            else:
                break
        except Exception as e:
            print("Failed to delete user. Exception occurred: {}".format(e))
            break



db_mgmt_init()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<ID %r; User %r;>' % (self.id, self.username)

    def get_user_password(self):
        return self.password


def database_add_user(username, password_plain_text):
    user = User(username=username, password=bcrypt.generate_password_hash(password_plain_text.encode("utf-8")))
    db.session.add(user)
    db.session.commit()


def database_delete_user_by_username(username):
    """
    Delete user from database

    :Args:
        username (str) the user's username to be deleted from the db
    """
    User.query.filter(User.username == username).delete()
    db.session.commit()


def database_delete_user_by_primary_key(key):
    User.query.get(key).delete()
    db.session.commit()

while True:
    opt = db_mgmt_ask_option()
    if not opt:
        list_all_users()
    elif opt == 1:
        add_user_wrapper()
    elif opt == 2:
        pass
    elif opt == 3:
        delete_user_wrapper_by_name()
    elif str(opt).lower() == "exit" or str(opt).lower() == "quit":
        raise SystemExit(0)
    print("\n")
