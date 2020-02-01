from fileshare.shared.database.database import db

class Directory(db.Model):
    rel_path: str     = db.Column(db.Unicode(512), primary_key=True, nullable=False)
    abs_path: str     = db.Column(db.Unicode(1024), unique=True, nullable=False)
    parent_path: str  = db.Column(db.Unicode(512))  # Can be nullable
    name: str         = db.Column(db.Unicode(128), nullable=False)
    content_dir: str  = db.Column(db.Text)  # Sub-directories of the directory, names only, splitted by ,
    content_file: str = db.Column(db.Text)  # Files in the directory, names only, splitted by ,
    last_mod: float   = db.Column(db.Float)
    dir_count: int    = db.Column(db.Integer)
    file_count: int   = db.Column(db.Integer)
    size: int         = db.Column(db.Integer, nullable=False)
    archive_name: str = db.Column(db.Unicode(16))
    archive_id: str   = db.Column(db.Unicode(32))
    archive_path: str = db.Column(db.Unicode(512))

    def __repr__(self):
        return "<Name: %r; Path Abs: %r; Path Rel: %r; Size: %r;>" % (self.name, self.abs_path, self.rel_path, self.size)
