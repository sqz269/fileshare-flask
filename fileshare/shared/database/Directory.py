from fileshare.shared.database.database import db

class Directory(db.Model):
    rel_path    = db.Column(db.Unicode(512), primary_key=True, nullable=False)
    abs_path    = db.Column(db.Unicode(1024), unique=True, nullable=False)
    parent_path = db.Column(db.Unicode(512))  # Can be nullable
    name        = db.Column(db.Unicode(128), nullable=False)
    content_dir = db.Column(db.Text)  # Sub-directories of the directory, names only, splitted by ,
    content_file= db.Column(db.Text)  # Files in the directory, names only, splitted by ,
    last_mod    = db.Column(db.Float)
    dir_count   = db.Column(db.Integer)
    file_count  = db.Column(db.Integer)
    size        = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Name: %r; Path Abs: %r; Path Rel: %r; Size: %r;>" % (self.name, self.abs_path, self.rel_path, self.size)
