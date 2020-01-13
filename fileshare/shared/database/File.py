from fileshare.shared.database.database import db

class File(db.Model):
    rel_path    = db.Column(db.Unicode(512), primary_key=True, nullable=False)
    abs_path    = db.Column(db.Unicode(1024), unique=True, nullable=False)
    parent_path = db.Column(db.Unicode(512), nullable=False)
    name        = db.Column(db.Unicode(128), nullable=False)
    last_mod    = db.Column(db.Float)
    size        = db.Column(db.Integer)
    mimetype    = db.Column(db.String(32))


    def __repr__(self):
        return "<Name: %r; Path Abs: %r; Path Rel: %r; Size: %r; Mime: %r>" % (self.name, self.abs_path, self.rel_path, self.size, self.mimetype)
