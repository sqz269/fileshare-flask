from flask import Blueprint, render_template, request, send_from_directory
from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs.paths import make_abs_path_from_url

api_admin = Blueprint("api_admin", url_prefix="/api/admin")

@api_admin.route("top_files")
def top_files():
    pass
