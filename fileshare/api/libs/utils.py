import jwt
import time
import json
from flask import Response, jsonify, Flask

# issued jwt looks like {"CREATED": <UNIX TIMESTAMP>, "VALIDFOR": <Seconds>}
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
        return (time.time() < (int(jwt_decoded["VALIDFOR"]) + int(jwt_decoded["CREATED"])))
    except jwt.InvalidSignatureError:
        return False


def jwt_issue(valid_length: int, key: str):
    """
    Generate a JWT contains the time the jwt is valid for, and the time it's generated

    :Args:
        valid_length (int) how long is the jwt will be valid for
        key (str) the secret key to encode the jwt with

    :Return:
        (Bytes) encoded jwt (returned by function jwt.encode)
    """
    return jwt.encode({"CREATED": time.time(), "VALIDFOR": int(valid_length)}, key)


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
