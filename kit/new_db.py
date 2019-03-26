from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import Flask

db_uri = input("Enter the path you want to create (Including the file name): ")
try:
    with open(db_uri, "w") as f:
        pass
except PermissionError:
    print("Failed to create file: Access Denied")

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app=app)
sqlite_db_uri = "sqlite:///" + db_uri
print("CREATING SQLITE DATABASE WITH URI: {}".format(sqlite_db_uri))
app.config.update({"SQLALCHEMY_DATABASE_URI": sqlite_db_uri})


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # last_login_date = db.Column(db.String(40), nullable=True)
    # last_login_addr = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return '<ID %r; User %r;>' % (self.id, self.username)

    def get_user_password(self):
        return self.password

    # def get_user_last_login_date(self):
    #     return self.last_login_date

    # def get_user_last_login_addr(self):
    #     return self.last_login_addr


def database_add_user(username, password_plain_text):
    user = User(username=username, password=bcrypt.generate_password_hash(password_plain_text.encode("utf-8")))
    db.session.add(user)
    db.session.commit()


def database_delete_user(username):
    """
    Delete user from database

    :Args:
        username (str) the user's username to be deleted from the db
    """
    User.query.filter(User.username == username).delete()
    db.session.commit()

print("INITIALIZING DATABASE AT: {}".format(sqlite_db_uri))

db.create_all()

print("Database has been created\n Please add a new default user")

while True:
    try:
        username = input("Username: ")
        password = input("Password: ")
        database_add_user(username, password)
        db.session.commit()
        new_usr = input("User {} has been added to the database\nAdd another one (y/n)?")
        if new_usr.lower() == "y":
            continue
        else:
            break
    except Exception as e:
        print("Failed to add new user. Exception occurred: {}".format(e))
        break
