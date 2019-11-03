from flask import Blueprint, render_template
from fileshare.libs.configurationMgr import ConfigurationMgr

import jwt

site = Blueprint("site", __name__, template_folder="templates", static_folder="static", static_url_path="/site/static")


ConfigMgr = ConfigurationMgr()


@site.route('/', defaults={'path': ''})
@site.route('/<path:path>')
def homepage(path):
	#if ConfigMgr.config.get("ACCESS_PASSWORD"):
	#	pass
	#else:
	return render_template("index.html")


@site.route('/password')
def password_page():
	return render_template("password.html")
