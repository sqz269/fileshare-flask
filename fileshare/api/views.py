from flask import Blueprint, request
from werkzeug import secure_filename

from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs import paths
from fileshare.api.libs.utils import *

from fileshare.api.libs.status_to_msg import STATUS_TO_MESSAGE, STATUS_TO_HTTP_CODE

import os

configuration = ConfigurationMgr()

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

@api.route("/access-password", methods=["POST"])
def process_access_password():
    # Password json looks like { "password": password }
    if configuration.config.get("ACCESS_PASSWORD"):  # If access_password is enabled
        try:
            password = request.get_json()
        except (KeyError, TypeError):
            return make_status_resp(2, STATUS_TO_MESSAGE[2], STATUS_TO_HTTP_CODE[2]) 

        if password["password"] == configuration.config.get("ACCESS_PASSWORD"):
            resp = make_status_resp(0, "Authorized", STATUS_TO_HTTP_CODE[0])
            resp.set_cookie("AccessToken", 
                            jwt_issue_access_token("/"),
                            max_age=int(configuration.config.get("JWT_VALID_FOR")))
            return resp
        
        else:
            return make_status_resp(3, STATUS_TO_MESSAGE[3], STATUS_TO_HTTP_CODE[3])
    else:
        return make_status_resp(1, "Access Password is not in use", STATUS_TO_HTTP_CODE[1])


# use like /api/access-token?path=<URLPath>
# URLPath is the path that the access token will be valid for
# for example if the URLPath is /myPresentation/group
# Any files in /myPresentation/group will be accessible with the token
# But files in /myDocs/own will not be accessible with the token
@api.route("/access-token", methods=["POST"])
def issue_access_password():
    path = get_url_param(request.args, "path")

    if not path:
        return make_status_resp(2, "Required url paramater 'path' is not provided", STATUS_TO_HTTP_CODE[2])

    if is_requirements_met_token_issue(request.cookies, path):
        return make_json_resp_with_status({"status": 0, 
                                           "details": "success", 
                                           "token": jwt_issue_access_token(path).decode()}, 200)
    else:
        # Might change to a clear message for case of user issued access token is disabled
        return make_status_resp(6, STATUS_TO_MESSAGE[6], STATUS_TO_HTTP_CODE[6])


@api.route("/access-token", methods=["OPTION"])
def get_access_token_settings():
    return make_json_resp_with_status({"token_in_url_param": configuration.config.get("TOKEN_IN_URL_PARAM"),
                                       "user_issued_token": configuration.config.get("USER_ISSUED_TOKEN"),
                                       "user_issue_token_require_auth": configuration.config.get("USER_ISSUE_TOKEN_AUTH_REQUIRED")}, 200)


@api.route("/login")
def login():
    pass


# File api should be accessed like
# /api/files?path=<path_of_file>
@api.route('files', methods=["POST"])
def list_dir():
    path = get_url_param(request.args, "path")

    if not is_access_token_valid(request.cookies, request.args, path):
        return make_status_resp(4, STATUS_TO_MESSAGE[4], STATUS_TO_HTTP_CODE[4])

    if not path:
        return make_status_resp(2, "Required url paramater 'path' is not provided", STATUS_TO_HTTP_CODE[2])

    try:
        dir_data = paths.list_files_from_url(path, configuration.config.get("SHARED_DIR"))
    except AssertionError:
        return make_status_resp(102, STATUS_TO_MESSAGE[102], STATUS_TO_HTTP_CODE[102])
    except FileNotFoundError:
        return make_status_resp(103, "target path: {} does not exist".format(path), STATUS_TO_HTTP_CODE[103])

    return make_json_resp_with_status(dir_data, 200)


# send PUT Request to files with argument path to specify the path
# and argument filename to specify the filename
# for example PUT /api/files?path=/example-path/&filename=test
# will upload a file to /example-path/ with the filename of test
@api.route('files', methods=["PUT"])
def upload():
    path = get_url_param(request.args, "path")

    # Some work around had to be used do to this bug: https://github.com/pallets/werkzeug/issues/875
    if not is_requirements_met_file("UPLOAD", request.cookies, path):
        return make_status_resp(6, STATUS_TO_MESSAGE[6], STATUS_TO_HTTP_CODE[6])


    if not path: 
        return make_status_resp(2, "Required url paramater 'path' is not provided", STATUS_TO_HTTP_CODE[2])

    dir_abs_path = paths.make_abs_path_from_url(path, configuration.config.get("SHARED_DIR"), False)

    files = request.files.getlist("File")

    for file in files:
        if configuration.config.get("SECURE_UPLOAD_FILENAME"):
            file_name = secure_filename(file.filename)
        else:
            file_name = file.filename
        dst_path = paths.make_abs_path_from_url(file_name, dir_abs_path.decode(), fix_nt_path=True)
        file.save(dst_path.decode())
    
    return make_status_resp(0, "File uploaded successfully", STATUS_TO_HTTP_CODE[0])


@api.route('files', methods=["DELETE"])
def delete():
    path = get_url_param(request.args, "path")

    if not is_requirements_met_file("DELETE", request.cookies, path):
        return make_status_resp(6, STATUS_TO_MESSAGE[6], STATUS_TO_HTTP_CODE[6])

    abs_path = paths.make_abs_path_from_url()


@api.route('folders', methods=["PUT"])
def new_folder():
    path = get_url_param(request.args, "path")

    if not is_requirements_met_file("MKDIR", request.cookies, path):
        return make_status_resp(6, STATUS_TO_MESSAGE[6], STATUS_TO_HTTP_CODE[6])

    if not path: 
        return make_status_resp(2, "Required url paramater 'path' is not provided", STATUS_TO_HTTP_CODE[2])

    try:
        dir_abs_path = paths.make_abs_path_from_url(path, configuration.config.get("SHARED_DIR"), False)
    except AssertionError:
        return make_status_resp(102, STATUS_TO_MESSAGE[102], STATUS_TO_HTTP_CODE[102])

    try:
        os.mkdir(dir_abs_path)
        return make_json_resp_with_status({"status": 0, "details": "Successfully created directory", "path": path, "lastmod": os.path.getmtime(dir_abs_path)}, 200)
    except FileExistsError:
        return make_status_resp(100, STATUS_TO_MESSAGE[100], STATUS_TO_HTTP_CODE[100])
    except PermissionError:
        return make_status_resp(101, STATUS_TO_MESSAGE[101], STATUS_TO_HTTP_CODE[101])
