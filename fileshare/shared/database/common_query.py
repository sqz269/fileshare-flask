import os
from typing import Union, Tuple

import magic

from fileshare import app
from fileshare.shared.database.database import db
from fileshare.shared.database.Directory import Directory
from fileshare.shared.database.File import File
from fileshare.shared.database.User import User


class CommonQuery:

    @staticmethod
    def query_user_by_username(username) -> User:
        return User.query.filter_by(username=username).first()


    @staticmethod
    def query_file_by_relative_path(path) -> File:
        return File.query.get(path)

    @staticmethod
    def query_file_by_name(file_name) -> list:
        return File.query.filter(name=file_name).all()


    @staticmethod
    def query_dir_by_relative_path(path) -> Directory:
        return Directory.query.get(path)


    @staticmethod
    def query_all_by_absolute_path(path) -> Tuple[Tuple[File], Tuple[Directory]]:
        """Query all records by their abs_path in the database by the start of path
            (Simplified?: Query all records by it's common_prefix of the path and the record's abs_path)

        Arguments:
            path {str} -- the path to match

        Returns:
            tuple -- first element contain a list of matching records that are in the File table
                        second element contains a list of matching records in the Directory table
        """
        files = File.query.filter(File.abs_path.startswith(path)).all()
        dirs = Directory.query.filter(Directory.abs_path.startswith(path)).all()
        return (files, dirs)


    @staticmethod
    def query_last_modified_item(push_context=True) -> float:
        if push_context:
            with app.app_context():
                lm_file = db.session.query(db.func.max(File.last_mod)).first()[0]
                lm_dir = db.session.query(db.func.max(Directory.last_mod)).first()[0]
        else:
            lm_file = db.session.query(db.func.max(File.last_mod)).first()[0]
            lm_dir = db.session.query(db.func.max(Directory.last_mod)).first()[0]

        return lm_file if lm_file > lm_dir else lm_dir



    @staticmethod
    def delete_dir_by_relative_path(path) -> Directory:
        """Deletes a directory record from the database

        Arguments:
            path {str} -- the relative path of the folder that is going to be deleted

        Returns:
            Directory -- the database entry for the deleted folder
        """
        folder = File.query.get(path)
        db.session.delete(folder)
        db.session.commit()
        return folder


    @staticmethod
    def delete_file_by_relative_path(path) -> File:
        """Deletes a file record from the database

        Arguments:
            path {str} -- the relative path of the file that is going to be deleted

        Returns:
            File -- the database entry for the deleted file
        """
        file = File.query.get(path)
        db.session.delete(file)
        db.session.commit()
        return file


    @staticmethod
    def insert_new_dir_record(parent_folder: Directory, name, commit=True) -> Directory:
        folder              = Directory()
        folder.name         = name
        folder.abs_path     = os.path.join(parent_folder.abs_path, name)
        folder.rel_path     = os.path.join(parent_folder.rel_path, name)
        folder.parent_path  = parent_folder.rel_path
        folder.content_dir  = ""
        folder.content_file = ""
        folder.dir_count    = 0
        folder.file_count   = 0
        folder.size         = 0

        db.session.add(folder)

        if commit:
            db.session.commit()


    @staticmethod
    def insert_new_file_record_ex(rel_path, name, size, last_mod, mime):
        pass


    @staticmethod
    def insert_new_file_record(parent_folder: Directory, name, commit=True) -> File:
        """Inserts a new file record into the file database

        A file must be already exist on the file system in order for this function to work
            This function is intended to be used with the upload view.
            The uploaded file will be first saved on to the computer,
            then it's parent dir's relative path (Upload destination)
            can be pass into this function to add the file uploaded to
            databases for display.

        Arguments:
            rel_path {str} -- the relative path (of parent directory) will points to the file
            name {str} -- name of the file
            commit {bool} -- True if you wish db.session.commit to be called within this function,
                            false to make the change be not not committed. which can be committed later (useful if you want to add a lot of files)
        """
        file            = File()
        file.abs_path   = os.path.join(parent_folder.abs_path, name)
        file.rel_path   = os.path.join(parent_folder.rel_path, name)
        file.parent_path= parent_folder.rel_path
        file.name       = name
        file.last_mod   = os.path.getmtime(file.abs_path)
        file.size       = os.path.getsize(file.abs_path)

        with open(file.abs_path, "rb") as f:
            file.mimetype   = magic.Magic(True).from_buffer(f.read(1024))

        db.session.add(file)

        if commit:
            db.session.commit()

        return file
