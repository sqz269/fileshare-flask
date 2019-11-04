from flask import Blueprint, render_template, request
from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs.utils import jwt_validate
import jwt

site = Blueprint("site", __name__, template_folder="templates", static_folder="static", static_url_path="/site/static")


configuration = ConfigurationMgr()


@site.route('/', defaults={'path': ''})
@site.route('/<path:path>')
def homepage(path):
	if configuration.config.get("ACCESS_PASSWORD"): # If password is required to access the page
		if 'AccessToken' in request.cookies:  # If AccessToken is present in cookies
			if jwt_validate(request.cookies["AccessToken"], configuration.config.get("JWT_SECRET_KEY")):  # If the AccessToken is still valid
				return render_template("index.html")  # Render file page
		return render_template("password.html")
	return render_template("index.html")
