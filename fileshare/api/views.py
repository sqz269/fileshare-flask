from flask import Blueprint, request

from fileshare.shared.database.common_query import CommonQuery

from fileshare.api.libs.status_to_msg import STATUS_TO_MESSAGE, STATUS_TO_HTTP_CODE
from fileshare.api.libs import api_utils

from fileshare.shared.libs import utils

from fileshare.shared.database.database import db

from fileshare import app

from sqlalchemy import exc  # Sqlalchemy exceptions
from werkzeug import secure_filename

import os

api = Blueprint("api", __name__, url_prefix="/api")

"""
Known Status returned by json
0 - Operation was successful
-
User Errors
1 - Feature is not in use
2 - Required data/fields are not provided
3 - Invalid Password/Login
4 - Access Token is invalid
5 - Login Token is invalid
6 - Login or Access Token is invalid

Resource Related Errors
100 - Resource with the same name already exist
101 - Access to resource has been denied by the Operating System
102 - Invalid/Illegal Path has been provided
103 - Path provided does not exist
"""
@api.route("/file", methods=["POST"])
@api.route("/folder", methods=["POST"])
def list_directory():
    path = utils.get_url_param(request.args, "path")
    target_type = utils.get_url_param(request.args, "type")

    if os.name == "nt":
        path = path.replace("/", "\\")

    directory = CommonQuery.query_dir_by_relative_path(path)

    if not directory:
        return utils.make_status_resp_ex(103)

    data = api_utils.db_list_files(directory, True) if target_type == "table" else api_utils.db_list_files(directory)
    return utils.make_json_resp_with_status(data, 200)


@api.route("/file", methods=["PUT"])
def upload():
    path = utils.get_url_param(request.args, "path")

    if os.name == "nt":
        path = path.replace("/", "\\")

    files = request.files.getlist("File")

    parent_dir = CommonQuery.query_dir_by_relative_path(path)
    if not parent_dir: return utils.make_status_resp_ex(103)

    for file in files:
        file_name = secure_filename(file.filename) if app.config["SECURE_UPLOAD_FILENAME"] else file.filename
        file_path = os.path.join(parent_dir.abs_path, file_name)  # Construct the new file's absolute path
        file.save(file_path)  # THe file have to be save before the database write cuz it needs to detect it's mime type
        print("Saving file to: {}".format(file_path))

        # Add the file into the parent directory's record
        parent_dir.content_file = parent_dir.content_file + f",{file_name}" # Comma separated

        CommonQuery.insert_new_file_record(parent_dir, file_name, commit=False)

    db.session.commit()  # Update the parent folder's database entry to match the newly added file names

    return utils.make_status_resp_ex(0)


@api.route("/folder", methods=["DELETE"])
@api.route("/file", methods=["DELETE"])
def delete():
    content = request.json

    targets = []

    for path in content["folder"]:
        if os.name == "nt": path = path.replace("/", "\\")
        folder = CommonQuery.query_dir_by_relative_path(path)
        if not folder:
            return utils.make_status_resp(103, f"Folder with path: {path} does not exist", STATUS_TO_HTTP_CODE[103])
        targets.append(folder)

    for path in content["file"]:
        if os.name == "nt": path = path.replace("/", "\\")
        file = CommonQuery.query_file_by_relative_path(path)
        if not file:
            return utils.make_status_resp(103, f"File with path: {path} does not exist", STATUS_TO_HTTP_CODE[103])
        targets.append(file)

    failed_to_delete = []  # A list to store list of relative path if os.removed failed to remove them
    failed_to_delete_reason = None

    for target in targets:
        if app.config["DELETE_MODE"] == 1:  # Remove the target both from the file system and the database
            try:
                api_utils.delete_file_or_directory_from_filesystem(target)
                api_utils.delete_file_or_directory_from_db(target)
            except PermissionError:
                failed_to_delete.append(target.rel_path)
                failed_to_delete_reason = 101
                continue

        elif app.config["DELETE_MODE"] == 2:  # Only Remove the target from the database not the filesystem
            api_utils.delete_file_or_directory_from_db(target)

    db.session.commit()

    if failed_to_delete:
        return utils.make_status_resp(0, f"Errors [{STATUS_TO_MESSAGE[failed_to_delete_reason]}] has prevented some file from being deleted. A total of {len(failed_to_delete)} files out of {len(targets)} failed to be deleted", STATUS_TO_HTTP_CODE[0])


    return utils.make_status_resp_ex(0)


@api.route("/folder", methods=["PUT"])
def folder():
    path = utils.get_url_param(request.args, "path")  # Folder's parent path
    name = utils.get_url_param(request.args, "name")  # new folder's name

    if os.name == "nt":
        path = path.replace("/", "\\")

    parent_dir = CommonQuery.query_dir_by_relative_path(path)
    if not parent_dir: return utils.make_status_resp_ex(103)  # Parent folder isn't valid

    name = secure_filename(name) if app.config["SECURE_UPLOAD_FILENAME"] else name

    CommonQuery.insert_new_dir_record(parent_dir, name, commit=False)

    parent_dir.content_dir = parent_dir.content_dir + f",{name}"

    try:
        db.session.commit()
    except exc.IntegrityError:
        return utils.make_status_resp_ex(100)

    return utils.make_status_resp_ex(0)
