from flask import Blueprint, jsonify, request

from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs import paths

configuration = ConfigurationMgr()

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/password", methods=["POST"])
def process_access_password():
	# Password json looks like { "password": password }
	if configuration.config.get("ACCESS_PASSWORD"):  # If access_password is enabled

		try:
			password = request.get_json()
		except KeyError:
			return jsonify({"status": 2, "details": "No password is provided"})

		if password["password"] == configuration.config.get("ACCESS_PASSWORD"):
			return jsonify({"status": 0, "details": "Authorized"})
	else:
		return jsonify({"status": 1, "details": "Access password is disabled"})


@api.route("/test")
def test():
    return "THIS IS A TEST"
