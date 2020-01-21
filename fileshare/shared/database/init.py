from fileshare.shared.database.database import db
from fileshare.shared.database.Directory import Directory
from fileshare.shared.database.File import File
# from fileshare.shared.database.User import User
from fileshare import app

from fileshare.shared.libs.file_index import index_file

import time
import json

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


def is_db_initalized(info_path: str) -> tuple:
    """Checks if the file database is initialized
    it helps to determin if we need to call prepare_db

    Arguments:
        info_path {str} -- the path like string that points the the infomation written by write_info function

    Return:
        tuple - with 2 element. first element (True/False) represents if the shareing paths are changed
                2nd element is a tuple contains 2 element,
                    first element in the tuple is a list of path shared that is missing since the last file index
                    second element in the tuple is a list of path shared that is added since the last file index
    """
    try:
        with open(info_path, "r") as file:
            info_json = json.load(file)
            paths_changed = False
            missing_paths = []
            extra_paths = []
            for path in info_json["paths_recorded"]:
                if path not in app.config["SHARED_DIRECTORY"]:
                    paths_changed = True
                    missing_paths.append(path)

            for path in app.config["SHARED_DIRECTORY"]:
                if path not in info_json["paths_recorded"]:
                    paths_changed = True
                    missing_paths.append(path)

            return (paths_changed, (missing_paths, extra_paths))
    except (FileNotFoundError, PermissionError):
        return (True, (app.config["SHARED_DIRECTORY"], []))


def write_info(path):
    with open(path, "w") as file:
        info_json = {
            "time_created": time.time(),
            "paths_recorded": app.config["SHARED_DIRECTORY"]
        }
        json.dump(info_json, file)


def init_db():
    preped = is_db_initalized("db_info.json")
    if preped[0]:
        print("Shared path changed. Missing paths: {}. New paths: {}".format(preped[1][0], preped[1][1]))
    else:
        print("Shared path did not change.")
        return;

    ctx = app.app_context()  # Crates an app context so the database can be edited
    ctx.push()

    db.create_all()
    print("Initializing database records")
    records_dir = 0
    records_file = 0

    index = []
    for path in app.config["SHARED_DIRECTORY"]:
        index.append(index_file(path))

    for indexed_files in index:
        for directory_data in indexed_files.values():
            entry = unpack_dir_info_to_db_entry(directory_data)
            db.session.add(entry)
            records_dir += 1
            for files_data in directory_data["file_content"].values():
                entry = unpack_file_info_to_db_entry(files_data)
                db.session.add(entry)
                records_file += 1

    # usr = User()
    # usr.id = 0
    # usr.username = "admin"
    # usr.password = "hunter2"
    # usr.permission = 0xb11111
    # db.session.add(usr)

    print(f"About to commit total of {records_dir + records_file} records. {records_file} file records. {records_dir} dir records. One Administrator Account record")
    db.session.commit()

    write_info("db_info.json")

    ctx.pop()

"""
Returned structure sample (file_index.py also have one)
{
    "D:\\PROG\\fileshare-flask\\.vscode": {
        "relative_path": "D:\\PROG\\fileshare-flask\\.vscode",
        "absolute_path": "D:\\PROG\\fileshare-flask\\.vscode",
        "name": ".vscode",
        "last_mod": 1575731299.6164553,
        "sub_dir_count": 22,
        "sub_file_count": 1197,
        "size": 82194107,
        "dir_content": [
            "cache"
        ],
        "file_content": {
            "D:\\PROG\\fileshare-flask\\.vscode\\c_cpp_properties.json": {
                "relative_path": "D:\\PROG\\fileshare-flask\\.vscode\\c_cpp_properties.json",
                "absolute_path": "D:\\PROG\\fileshare-flask\\.vscode\\c_cpp_properties.json",
                "name": "c_cpp_properties.json",
                "last_mod": 1575734872.063939,
                "size": 1537,
                "mimetype": "text/plain"
            },
            "D:\\PROG\\fileshare-flask\\.vscode\\launch.json": {
                "relative_path": "D:\\PROG\\fileshare-flask\\.vscode\\launch.json",
                "absolute_path": "D:\\PROG\\fileshare-flask\\.vscode\\launch.json",
                "name": "launch.json",
                "last_mod": 1573789875.4484072,
                "size": 887,
                "mimetype": "text/plain"
            },
            "D:\\PROG\\fileshare-flask\\.vscode\\settings.json": {
                "relative_path": "D:\\PROG\\fileshare-flask\\.vscode\\settings.json",
                "absolute_path": "D:\\PROG\\fileshare-flask\\.vscode\\settings.json",
                "name": "settings.json",
                "last_mod": 1575061423.5391603,
                "size": 514,
                "mimetype": "text/plain"
            }
        }
    },
    ...
}
"""
