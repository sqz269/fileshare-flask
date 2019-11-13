import os
import jwt
import time
import json
from flask import Response, jsonify, Flask
from fileshare.libs.configurationMgr import ConfigurationMgr

configuration = ConfigurationMgr()


def get_url_param(url_params, target_param):
    """
    Get a url paramater's value, unlike requests.args.get
    this function will return None if the paramater doesn't exist instead rasing a exception

    :Args:
        url_params (request.args) dictionary of paramaters
        target_param (str) the paramater to retreive

    :Return:
        (str) if the paramater exists else returns None
    """
    try:
        return url_params[target_param]
    except:
        return None


def is_access_token_valid(cookies, path) -> bool:
    """
    Check if an access token (required by configuration "ACCESS_PASSWORD") is a valid token
    Unlink is_access_token_valid this function also check

    :Args:
        cookies (request.cookies -> dict) dictionary of cookies

    :Return:
        (bool) True if the access token is valid, false if it is not
    """
    if configuration.config.get("ACCESS_PASSWORD"):
        if 'AccessToken' in cookies:
            return jwt_validate_access_token(cookies["AccessToken"], 
                                            configuration.config.get("JWT_SECRET_KEY"), 
                                            path)
        return False

    return True


def is_access_token_valid_no_path(cookies) -> bool:
    """
    Check if an access token (required by configuration "ACCESS_PASSWORD") is a valid token
    Invokes is_access_token_valid with path paramater set to "/"

    :Args:
        cookies (request.cookies -> dict) dictionary of cookies

    :Return:
        (bool) True if the access token is valid, false if it is not
    """
    if configuration.config.get("ACCESS_PASSWORD"):
        if "AccessToken" in cookies:
            return jwt_validate(cookies["AccessToken"], configuration.config.get("JWT_SECRET_KEY"))
    return False


def is_login_token_valid(cookies) -> bool:
    if "LoginToken" in cookies:
        return jwt_validate(cookies['LoginToken'],
                            configuration.config.get('JWT_SECRET_KEY'))
    return False


def is_requirements_met_file(operation, cookies, path):
    """
    Check if all privilege requirements are satisfied to change the file

    :Args:
        operation (string) - the the way the file will be changed; avaliable fields: (UPLOAD, DELETE, RENAME, MKDIR)
    
        cookies (request.cookies) - the cookies the user send with the request, used to verify login/access token

        path (str) - the file path the operation is requested to change

    :Return:
        (bool) true if the user have all the privilege to change the file, else False
    """
    ops_to_privilege_name = {
        "UPLOAD": "UPLOAD_AUTH_REQUIRED",
        "DELETE": "DELETE_AUTH_REQUIRED",
        "RENAME": "RENAME_AUTH_REQUIRED",
        "MKDIR": "MKDIR_AUTH_REQUIRED"
    }

    current_privilege = [is_access_token_valid(cookies, path), is_login_token_valid(cookies)]

    is_access_password_enabled = configuration.config.get("ACCESS_TOKEN") == True
    # Convert the string to boolean to keep consistency at required_privilege

    required_privilege = [is_access_password_enabled,
                        configuration.config.get(ops_to_privilege_name[operation])] # [AccessPrivilege, LoginPrivilege]

    for (required_priv, current_priv) in zip(required_privilege, current_privilege):
        if not ((required_priv == current_priv) or (current_priv)):
        # if the user does not have required privliege or they have the privliege but the server does not require the pri
            return False
    
    return True


def is_requirements_met_token_issue(cookies, path):
    """
    Check if all privilege requirements are satisfied to issue a temporary access token

    :Args:
        operation (string) - the the way the file will be changed; avaliable fields: (UPLOAD, DELETE, RENAME, MKDIR)
    
        cookies (request.cookies) - the cookies the user send with the request, used to verify login/access token

    :Return:
        (bool) true if the user have all the privilege to issue a temporary access token
    """
    allow_user_issue_token = configuration.config.get("USER_ISSUED_TOKEN")
    user_issue_toke_auth_required = configuration.config.get("USER_ISSUE_TOKEN_AUTH_REQUIRED")

    if not allow_user_issue_token: return False

    if user_issue_toke_auth_required:
        if not is_login_token_valid(cookies) and not is_access_token_valid(cookies, path):
            return False

    else:
        if not is_access_token_valid(cookies, path):
            return False

    return True


def jwt_validate_access_token(src_jwt: str, key: str, current_path: str):
    try:
        jwt_decoded = jwt.decode(src_jwt, key)
        is_path_valid = os.path.commonprefix((current_path, jwt_decoded["PATH"])) == jwt_decoded["PATH"]
        return (time.time() < (int(configuration.config.get("JWT_VALID_FOR")) + int(jwt_decoded["iat"]))) and (is_path_valid)
    except:
        return False


def jwt_issue_access_token(allow_path):
    return jwt_issue(configuration.config.get("JWT_SECRET_KEY"),
                     extra_fields={"PATH": allow_path})


# issued jwt looks like {"iat": <UNIX TIMESTAMP>}
def jwt_validate(src_jwt: str, key: str) -> bool:
    """
    Check if a jwt is valid

    :Args:
        src_jwt (string/bytes) the jwt that it's validation status needs to be checked
        key (str) the secret key that used to encrypt the jwt

    :Return:
        (bool) True if the jwt has not expired, False if it did or it's invalid
    """
    try:
        jwt_decoded = jwt.decode(src_jwt, key)
        return (time.time() < (configuration.config.get("JWT_VALID_FOR")) + int(jwt_decoded["iat"]))
    except jwt.InvalidSignatureError:
        return False


def jwt_issue(key: str, extra_fields={}):
    """
    Generate a JWT contains the time the jwt is valid for, and the time it's generated

    :Args:
        valid_length (int) how long is the jwt will be valid for
        key (str) the secret key to encode the jwt with

    :Return:
        (Bytes) encoded jwt (returned by function jwt.encode)
    """
    payload = {"iat": time.time()}
    payload.update(extra_fields)
    return jwt.encode(payload, key)


def make_status_resp(status, details, http_resp):
    return make_json_resp_with_status({"status": status, "details": details}, http_resp)


def make_json_resp_with_status(data: dict, status: int) -> Response:
    """
    Creates a response object with at status code and json
    the mimetype will be 'application/json'

    :Arg:
        json (dict) the data with be send with the response
        status (int) the http status the response will be

    :Return:
        (flask.Response) flask.Response object with json payload and a http status
    """
    return Response(
        response=json.dumps(data),
        status=status,
        mimetype="application/json"
    )
