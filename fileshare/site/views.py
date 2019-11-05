from flask import Blueprint, render_template, request
from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs.utils import jwt_validate, is_access_token_valid
import jwt

site = Blueprint("site", __name__, template_folder="templates", static_folder="static", static_url_path="/site/static")


configuration = ConfigurationMgr()


@site.route('/', defaults={'path': ''})
@site.route('/<path:path>')
def homepage(path):
    if configuration.config.get("ACCESS_PASSWORD"):
        if is_access_token_valid(request.cookies):
            return render_template("index.html")
        else:
            return render_template("password.html")
    else:
        return render_template("index.html")
