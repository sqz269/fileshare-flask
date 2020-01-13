from fileshare.shared.database.database import db

class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(80), unique=True, nullable=False)
    password    = db.Column(db.String(80), unique=True, nullable=False)
    permission  = db.Column(db.BINARY(5), nullable=False)

    def get_user_password(self):
        return self.password

    def get_user_permission(self):
        return self.permission

    def __repr__(self):
        return "<ID: %r; Username: %r; Permission: %r>" % (self.id, self.username, self.permission)
