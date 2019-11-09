from flask import Blueprint, request
from werkzeug import secure_filename

from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs import paths
from fileshare.api.libs.utils import make_json_resp_with_status,jwt_issue, is_access_token_valid, is_requirements_met

configuration = ConfigurationMgr()

api = Blueprint("api", __name__, url_prefix="/api")

"""
Known Status returned by json
0 - Operation was successful
1 - Feature is not in use
2 - Required data/fields are not provided
3 - Invalid Password/Login
4 - Access Token is invalid
5 - Login Token is invalid
6 - Login Token or Access Token is invalid
"""

@api.route("/access-password", methods=["POST"])
def process_access_password():
    # Password json looks like { "password": password }
    if configuration.config.get("ACCESS_PASSWORD"):  # If access_password is enabled

        try:
            password = request.get_json()
        except (KeyError, TypeError):
            return make_json_resp_with_status({"status": 2, "details": "No password is provided"}, 401)

        if password["password"] == configuration.config.get("ACCESS_PASSWORD"):
            resp = make_json_resp_with_status({"status": 0, "details": "Authorized"}, 200)
            resp.set_cookie("AccessToken", jwt_issue(configuration.config.get("JWT_VALID_FOR"),
                                                     configuration.config.get("JWT_SECRET_KEY")), max_age=int(configuration.config.get("JWT_VALID_FOR")))
            return resp
        else:
            return make_json_resp_with_status({"status": 3, "details": "Invalid password"}, 401)
    else:
        return make_json_resp_with_status({"status": 1, "details": "Access password is disabled"}, 400)


@api.route("/login")
def login():
    pass


# File api should be accessed like
# /api/files?path=<path_of_file>
@api.route('files', methods=["POST"])
def list_dir():
    if configuration.config.get("ACCESS_PASSWORD"):
        if not is_access_token_valid(request.cookies):
            return make_json_resp_with_status({"status": 4, "details": "Access Token is invalid/expired"}, 401)

    try:
        path = request.args.get('path')  # Get the argument <url>?path=
    except:
        path = None

    if not path:
        return make_json_resp_with_status({"status": 2, "details": "Required url paramater 'path' is not provided"}, 400)

    dir_data = paths.list_files_from_url(path, configuration.config.get("SHARED_DIR"))
    return make_json_resp_with_status(dir_data, 200)


# send PUT Request to files with argument path to specify the path
# and argument filename to specify the filename
# for example PUT /api/files?path=/example-path/&filename=test
# will upload a file to /example-path/ with the filename of test
@api.route('files', methods=["PUT"])
def upload():
    # Some work around had to be used do to this bug: https://github.com/pallets/werkzeug/issues/875
    if not is_requirements_met("UPLOAD", request.cookies):
        return make_json_resp_with_status({"status": 6, "details": "Login Token or Access Token is invalid"}, 401)
    
    try:
        path = request.args.get("path")
    except:
        path = None

    if not path: return make_json_resp_with_status({"status": 2, "details": "Required url paramater 'path' is not provided"}, 400)

    dir_abs_path = paths.make_abs_path_from_url(path, configuration.config.get("SHARED_DIR"))

    files = request.files.getlist("File")

    for file in files:
        if configuration.config.get("SECURE_UPLOAD_FILENAME"):
            file_name = secure_filename(file.filename)
        else:
            file_name = file.filename
        dst_path = paths.make_abs_path_from_url(file_name, dir_abs_path, fix_nt_path=True)
        file.save(dst_path.decode())
    
    return make_json_resp_with_status({"status": 0, "details": "Files uploaded successfully"}, 200)


@api.route('files', methods=["POST"])
def delete():
    if is_requirements_met("DELETE", request.cookie):
        pass


@api.route('folders', methods=["PUT"])
def new_folder():
    if not is_requirements_met("MKDIR", request.cookies):
        return make_json_resp_with_status({"status": 6, "details": "Login Token or  Access Token is invalid"}, 401)

    
