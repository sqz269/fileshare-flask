import os
from typing import Tuple

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from fileshare import app
from fileshare.shared.database.common_query import CommonQuery
from fileshare.shared.database.database import db
from fileshare.shared.database.Directory import Directory
from fileshare.shared.database.File import File
from fileshare.shared.libs.file_index import index_file


def unpack_dir_info_to_db_entry(data: dict) -> Directory:
    """Unpacks a file index result about a directory to a database entry

    Arguments:
        data {dict} -- The value of a directory record that is returned by index_file

    Returns:
        Directory -- The database entry that represents the directory
    """
    entry = Directory()
    entry.abs_path      = data["absolute_path"]
    entry.rel_path      = data["relative_path"]
    entry.parent_path   = data["parent_path"]
    entry.name          = data["name"]
    entry.last_mod      = data["last_mod"]
    entry.size          = data["size"]
    entry.dir_count     = data["sub_dir_count"]
    entry.file_count    = data["sub_file_count"]
    entry.content_dir   = ",".join(data["dir_content"])
    entry.content_file  = ",".join([value["name"] for value in data["file_content"].values()])
    entry.archive_id    = None
    entry.archive_name  = None
    entry.archive_path  = None
    # Because the file_content is a dictionary so we want to extra the names of the file and put it in a list
    return entry


def unpack_file_info_to_db_entry(data: dict) -> File:
    """Unpacks a file index result about a file to a database entry

    Arguments:
        data {[type]} -- [description]

    Returns:
        File -- The database entry that represents the file
    """
    entry = File()
    entry.abs_path      = data["absolute_path"]
    entry.rel_path      = data["relative_path"]
    entry.parent_path   = data["parent_path"]
    entry.name          = data["name"]
    entry.last_mod      = data["last_mod"]
    entry.size          = data["size"]
    entry.mimetype      = data["mimetype"]
    return entry


def remove_shared_path_from_db(path: str):
    app.logger.info(f"Removing all record with abs_path starting with: {path}")

    removed_dirs = 0
    removed_files = 0

    entry_files, entry_dirs = CommonQuery.query_all_by_absolute_path(path)
    for entry in entry_files:
        db.session.delete(entry)
        removed_files += 1

    for entry in entry_dirs:
        db.session.delete(entry)
        removed_dirs += 1

    app.logger.info(f"About to commit a total of {removed_files + removed_dirs} less records. {removed_files} less file records. {removed_dirs} less dir records.")


def add_shared_path_to_db(path: str):
    """Add all contents in a path to database

    Arguments:
        path {str} -- the path to record things from
    """
    app.logger.info(f"Adding path: {path} to database")

    records_dir = 0
    records_file = 0

    indexed_files = index_file(path)

    for directory_data in indexed_files.values():
        entry = unpack_dir_info_to_db_entry(directory_data)
        db.session.add(entry)
        records_dir += 1

        for files_data in directory_data["file_content"].values():
            entry = unpack_file_info_to_db_entry(files_data)
            db.session.add(entry)
            records_file += 1

    app.logger.info(f"About to commit total of {records_dir + records_file} records. {records_file} file records. {records_dir} dir records.")

    db.session.commit()


def _find_potential_dir_with_removed_items(directory: str, last_update_time: float, indexed_files: dict) -> list:
    potential_dirs = []
    for directory_data in indexed_files.values(): # Loop through all the directories
        potential_deleted_item = True
        if directory_data["last_mod"] >= last_update_time: # if the directory were modified after the last record in the database
            for files_data in directory_data["file_content"].values():  # And if the updated modified date is due to a update of a file of a subdirectory
                if files_data["last_mod"] == directory_data["last_mod"]:
                    potential_deleted_item = False
                    break
            if potential_deleted_item: potential_dirs.append(directory_data["absolute_path"])

    return potential_dirs


def _match_for_removed_item_and_delete(directory: str):
    """checks for any deleted file from the database
        if a file was deleted on the filesystem, it will
        delete the record for the database

    Arguments:
        directory {str} -- the path to check for any deleted files
    """
    files_entry, dirs_entry = CommonQuery.query_all_by_absolute_path(directory)
    for entry in files_entry:
        if not os.path.exists(entry):
            app.logger.debug(f"Found missing directory with path: {entry.abs_path}")
            db.session.delete(entry)

    for entry in dirs_entry:
        if not os.path.exists(entry):
            app.logger.debug(f"Found missing file with path: {entry.abs_path}")
            db.session.delete(entry)


def scan_and_update_deleted_files(path: str, last_update_time: float, indexed_files: dict):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path): continue

        if os.path.getmtime(item_path) > last_update_time:
            potential_paths = _find_potential_dir_with_removed_items(item_path, last_update_time, indexed_files)
            for paths in potential_paths:
                _match_for_removed_item_and_delete(path)


def scan_and_update_new_files(path: str, last_update_time: float, indexed_files: dict):
    """Update contents in the path that already exist in the database
        useful when file are move to the shared folder locally and add it to the database
        This function does not push any app context, use it in view function or call app.app_context().push

    Arguments:
        path {str} -- the folder to look for the new file/folder
        last_update_time {float} -- the last mod date of the last uploaded item in the database. should be get_last_modified_item
    """
    added_file = 0
    added_dirs = 0

    for directory_data in indexed_files.values():
        if directory_data["last_mod"] > last_update_time:
            # Behavior: Modifying an item with in a directory will only modify
            # it's parent's directory's last modified date, will not change
            # it's grandeparent's last mod date
            try:
                entry = unpack_dir_info_to_db_entry(directory_data)
                app.logger.debug(f"Found new directory with path: {entry.abs_path}")
                db.session.add(entry)
                added_dirs += 1
            except IntegrityError:  # TODO: Update the last mod time of the entry
                continue
        for files_data in directory_data["file_content"].values():
            if files_data["last_mod"] > last_update_time:
                try:
                    entry = unpack_file_info_to_db_entry(files_data)
                    app.logger.debug(f"Found new file with path: {entry.abs_path}")
                    db.session.add(entry)
                    added_file += 1
                except IntegrityError:
                    continue

    app.logger.info(f"About to commit total of {added_file + added_dirs} records. Added {added_file} file records. Added {added_dirs} dir records.")

    db.session.commit()


def is_database_initalized() -> bool:
    required_tables = ["directory", "file", "user"]
    engine = db.get_engine(app)
    for table in required_tables:
        if not engine.has_table(table): return False

    return True
