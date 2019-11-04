from flask import Blueprint, jsonify, request

from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs import paths
from fileshare.api.libs.utils import make_json_resp_with_status, jwt_validate, jwt_issue

configuration = ConfigurationMgr()

api = Blueprint("api", __name__, url_prefix="/api")

"""
Known Status returned by json
0 - Operation was successful
1 - Feature is not in use
2 - Required data/fields are not provided
3 - Invalid Password/Login
"""

@api.route("/password", methods=["POST"])
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


@api.route("/test")
def test():
    return "THIS IS A TEST"
