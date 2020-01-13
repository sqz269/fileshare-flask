from flask import Response
import json

from fileshare.api.libs.status_to_msg import STATUS_TO_HTTP_CODE, STATUS_TO_MESSAGE

def get_url_param(url_params: dict, target_param: str) -> str:
    """Get a url paramater's value, unlike requests.args.get
    this function will return None if the paramater doesn't exist instead of rasing a exception

    
    Arguments:
        url_params {request.args/dict} -- dictionary of paramaters
        target_param {str} -- the paramater to retreive
    
    Returns:
        [str] -- returns the value of the item if the paramater exists else returns empty string
    """
    try:
        return url_params[target_param]
    except:
        return ""


def get_cookie_value(cookies, cookie_name):
    """Get's a cookies value

        
    Arguments:
        cookies {request.cookies/dict} -- dictionary of cookies
        cookie_name {str} -- the cookies to retreive
    
    Returns:
        [str] -- returns the value of the item if the cookies exists else returns empty string
    """
    try:
        return cookies[cookie_name]
    except:
        return ""


def make_status_resp(status, details, http_resp):
    return make_json_resp_with_status({"status": status, "details": details}, http_resp)


def make_status_resp_ex(status_code):
    return make_status_resp(status_code, STATUS_TO_MESSAGE[status_code], STATUS_TO_HTTP_CODE[status_code])


def make_json_resp_with_status(data: dict, status: int) -> Response:
    """Creates a response object with at status code and json
    the mimetype will be 'application/json'
    
    Arguments:
        data {dict} -- the data with be send with the response
        status {int} -- the http status the response will be
    
    Returns:
        flask.Response -- flask.Response object with json payload and a http status
    """
    return Response(
        response=json.dumps(data),
        status=status,
        mimetype="application/json"
    )
