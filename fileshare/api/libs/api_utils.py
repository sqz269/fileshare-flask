from fileshare.shared.database.Directory import Directory
from fileshare.shared.database.File import File

from fileshare.shared.database.database import db

from fileshare.shared.database.common_query import CommonQuery

import os
import shutil

from typing import Union


def name_to_html_link(name, path, is_file):
    TEMPLATE_DIRECTORY = f"""<a href="javascript:changeDirectory('{path}')">{name}</a>"""
    TEMPLATE_FILE = f"""<a href="{path}">{name}</a>"""
    if is_file:
        return TEMPLATE_FILE
    return TEMPLATE_DIRECTORY


def db_list_files(record: Directory, for_bootstrap_tables=False) -> dict:
    
    content = {"dirs": [], "files": []}
    if record.content_dir:
        for folder in record.content_dir.split(","):
            dir_rel_path    = os.path.join(record.rel_path, folder)
            dir_info        = CommonQuery.query_dir_by_relative_path(dir_rel_path)
            
            if for_bootstrap_tables:
                name = name_to_html_link(dir_info.name, 
                                        dir_info.rel_path.replace("\\", "/"), 
                                        False)
            else:
                name = dir_info.name

            content["dirs"].append({
                    "name"      : name,
                    "path"      : dir_info.rel_path.replace("\\", "/"),
                    "size"      : dir_info.size,
                    "last_mod"  : dir_info.last_mod,
                    "dir_count" : dir_info.dir_count,
                    "file_count": dir_info.file_count
            })

    if record.content_file:
        for file in record.content_file.split(","):
            file_rel_path = os.path.join(record.rel_path, file)
            file_info = CommonQuery.query_file_by_relative_path(file_rel_path)

            if for_bootstrap_tables:
                name = name_to_html_link(file_info.name, 
                                        file_info.rel_path.replace("\\", "/"), 
                                        True)
            else:
                name = file_info.name


            content["files"].append({
                    "name"      : name,
                    "path"      : file_info.rel_path.replace("\\", "/"),
                    "size"      : file_info.size,
                    "last_mod"  : file_info.last_mod,
                    "mimetype"  : file_info.mimetype
            })

    parent_path = record.rel_path.replace("\\", "/")
    return {parent_path: content}


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
