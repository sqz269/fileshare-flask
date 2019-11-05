from flask import Blueprint, jsonify, request
from werkzeug import secure_filename

from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs import paths
from fileshare.api.libs.utils import make_json_resp_with_status, jwt_validate, jwt_issue, is_access_token_valid

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
    path = request.args.get('path')
    if not path:
        return make_json_resp_with_status({"status": 2, "details": "Required url paramater 'path' is not provided"}, 400)

    if configuration.config.get("ACCESS_PASSWORD"):
        if not is_access_token_valid(request.cookies):
            return make_json_resp_with_status({"status": 4, "details": "Access Token is invalid/expired"}, 401)

    dir_data = paths.list_files_from_url(path, configuration.config.get("SHARED_DIR"))
    return make_json_resp_with_status(dir_data, 200)


@api.route('files', methods=["PUT"])
def upload():
    pass


@api.route('files', methods=["POST"])
def delete():
    pass
