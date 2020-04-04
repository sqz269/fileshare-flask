from fileshare.shared.database.Directory import Directory
from fileshare.shared.database.File import File

from fileshare.shared.database.database import db

from fileshare.shared.database.common_query import CommonQuery

from fileshare.api.libs.bootstrap_table_html import BootstrapTableHtmlFormatter

from fileshare import app

from fileshare.shared.libs import utils
import hashlib

import os
import shutil

from typing import Union


def db_list_directory_basic(record: Directory) -> dict:
    content = {"dirs": [], "files": []}
    if record.content_dir:
        for folder in record.content_dir.split(","):
            dir_rel_path    = os.path.join(record.rel_path, folder)
            dir_info        = CommonQuery.query_dir_by_relative_path(dir_rel_path)

            content["dirs"].append({
                    "name"      : dir_info.name,
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

            content["files"].append({
                    "name"      : file_info.name,
                    "path"      : file_info.rel_path.replace("\\", "/"),
                    "size"      : file_info.size,
                    "last_mod"  : file_info.last_mod,
                    "mimetype"  : file_info.mimetype
            })

    parent_path = record.rel_path.replace("\\", "/")
    return {parent_path: content}


def db_list_directory_bootstrap_table(record: Directory) -> dict:
    contents = db_list_directory_basic(record)

    for dir_content in contents.values():
        for folder_contained in dir_content["dirs"]:
            folder_contained.update({"name_raw": folder_contained["name"]})
            folder_contained["name"] = BootstrapTableHtmlFormatter.name_to_html_link(folder_contained["name"], folder_contained["path"], False)
            folder_contained.update({"ops": BootstrapTableHtmlFormatter.generate_ops(folder_contained["name"], folder_contained["path"], False)})

        for file_contained in dir_content["files"]:
            file_contained.update({"name_raw": file_contained["name"]})
            file_contained["name"] = BootstrapTableHtmlFormatter.name_to_html_link(file_contained["name"], file_contained["path"], True)
            file_contained.update({"ops": BootstrapTableHtmlFormatter.generate_ops(file_contained["name"], file_contained["path"], True)})

    return contents


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

# Can be merged into one function with delete_file_from_db
def delete_dir_from_db(directory: Directory, commit=False):
    parent = CommonQuery.query_dir_by_relative_path(directory.parent_path)
    content_dir_list = parent.content_dir.split(",")
    content_dir_list.remove(directory.name)
    parent.content_dir = ",".join(content_dir_list)

    db.session.delete(directory)

    if commit:
        db.session.commit()


def generate_and_register_archive(directory: Directory, commit=False) -> None:
    directory.archive_id = hashlib.md5(directory.abs_path.encode()).hexdigest()

    zip_dst = os.path.join(app.config["ARCHIVE_STOREAGE_DIRECTORY"], directory.archive_id)
    directory.archive_path = zip_dst
    directory.archive_name = f"{directory.name}.zip"

    utils.generate_archive(directory.abs_path, directory.archive_path)

    if commit:
        db.session.commit()
