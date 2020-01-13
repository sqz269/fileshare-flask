from fileshare.shared.database.Directory import Directory
from fileshare.shared.database.File import File

from fileshare.shared.database.database import db

from fileshare.shared.database.common_query import CommonQuery

import os
import shutil

from typing import Union

def db_directory_to_api_resp(record: Directory) -> dict:
    content = {}

    if record.content_dir: 
        # If they contains directories.
        # without this check an empty string (no contents that is a folder) can exist and split will return [] which makes the query can't find anything
        # which it just means the directory doesn't contain any folders
        for folder in record.content_dir.split(","):
            dir_rel_path = os.path.join(record.rel_path, folder)
            dir_info = CommonQuery.query_dir_by_relative_path(dir_rel_path)
            content.update({
                dir_info.name: {
                    "name"      : dir_info.name,
                    "isDir"     : True,
                    "path"      : dir_info.rel_path.replace("\\", "/"),
                    "size"      : dir_info.size,
                    "last_mod"  : dir_info.last_mod,
                    "dir_count" : dir_info.dir_count,
                    "file_count": dir_info.file_count
                }
            })

    if record.content_file:
        for file in record.content_file.split(","):
            file_rel_path = os.path.join(record.rel_path, file)
            file_info = CommonQuery.query_file_by_relative_path(file_rel_path)
            content.update({
                file_info.name: {
                    "name"      : file_info.name,
                    "isDir"     : False,
                    "path"      : file_info.rel_path.replace("\\", "/"),
                    "size"      : file_info.size,
                    "last_mod"   : file_info.last_mod,
                    "mimetype"  : file_info.mimetype
                }
            })

    parent = record.rel_path.replace("\\", "/")

    return {parent: content}


def delete_file_or_directory_from_filesystem(entry: Union[Directory, File]):
    """Deletes a file or a directory from the filesystem permanently
    
    Arguments:
        entry {Union[Directory, File]} -- The database entry that represents the file/directory that is going to be deleted
    """
    if isinstance(entry, Directory):
        shutil.rmtree(entry.abs_path)
    elif isinstance(entry, File):
        os.remove(entry.abs_path)
    else:
        raise TypeError("argument entry match neither type File/Directroy")



def delete_file_or_directory_from_db(entry: Union[Directory, File], commit=False):
    """Delete either a file or directory entry from the database
    
    Arguments:
        entry {Union[Directory, File]} -- The entry you want to delete
    """
    if isinstance(entry, Directory):
        delete_dir_from_db(entry, commit)
    elif isinstance(entry, File):
        delete_file_from_db(entry, commit)
    else:
        raise TypeError("argument entry match neither type File/Directroy")


def delete_file_from_db(file: File, commit=False):
    parent = CommonQuery.query_dir_by_relative_path(file.parent_path)
    content_file_list = parent.content_file.split(",")
    content_file_list.remove(file.name)
    parent.content_file = ",".join(content_file_list)

    db.session.delete(file)

    if commit:
        db.session.commit()


def delete_dir_from_db(directory: Directory, commit=False):
    parent = CommonQuery.query_dir_by_relative_path(directory.parent_path)
    content_dir_list = parent.content_dir.split(",")
    content_dir_list.remove(directory.name)
    parent.content_dir = ",".join(content_dir_list)

    db.session.delete(directory)

    if commit:
        db.session.commit()
