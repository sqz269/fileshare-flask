import json
import time
from typing import List, Tuple

from fileshare import app
from fileshare.shared.database.common_query import CommonQuery
from fileshare.shared.database.database import db
from fileshare.shared.database.db_utils import (add_shared_path_to_db,
                                                remove_shared_path_from_db,
                                                scan_and_update_deleted_files,
                                                scan_and_update_new_files,
                                                is_database_initalized)
from fileshare.shared.libs.file_index import index_file


def get_missing_paths() -> Tuple[List[str], List[str]]:
    try:
        with open("db_info.json", "r") as file:
            info_json = json.load(file)

            paths_recorded: list = info_json["paths_recorded"]
            missing_paths = []
            extra_paths = []
            for path in paths_recorded:
                if path not in app.config["SHARED_DIRECTORY"]:
                    extra_paths.append(path)

            for path in app.config["SHARED_DIRECTORY"]:
                if path not in paths_recorded:
                    missing_paths.append(path)

        return (extra_paths, missing_paths)
    except FileNotFoundError:
        return ([], app.config["SHARED_DIRECTORY"])


def write_info(path):
    with open(path, "w") as file:
        info_json = {
            "time_created": time.time(),
            "paths_recorded": app.config["SHARED_DIRECTORY"]
        }
        json.dump(info_json, file)


def init_db():
    # TODO: Determin if database has been initalized or not
    # if not, we have to call db.create_all()
    with app.app_context():
        if not is_database_initalized():
            db.create_all()
        app.logger.info("Initializing database records")

        extra_paths, missing_paths = get_missing_paths()
        if not extra_paths and not missing_paths:
            app.logger.info("Shared path did not change from previous run")

        for path in extra_paths: remove_shared_path_from_db(path)
        for path in missing_paths: add_shared_path_to_db(path)

        write_info("db_info.json")

        db_last_mod = CommonQuery.query_last_modified_item(push_context=False)
        for path in app.config["SHARED_DIRECTORY"]:
            indexed_files = index_file(path)
            scan_and_update_deleted_files(path, db_last_mod, indexed_files)
            scan_and_update_new_files(path, db_last_mod, indexed_files)

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
