from flask import Blueprint, render_template, request, send_from_directory
from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs.utils import is_access_token_valid, get_url_param, is_access_token_valid_no_path
from fileshare.api.libs.paths import make_abs_path_from_url

admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static", static_url_path="/admin/static")

@admin.route("/admin")
def admin_panel():
    return render_template("admin.html")

@admin.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
