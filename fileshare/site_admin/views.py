from flask import Blueprint, render_template

site_admin = Blueprint("admin_site", __name__, url_prefix="/admin",template_folder="template", static_folder="static", static_url_path="/admin/static")

@site_admin.route("/")
def admin():
    return render_template("index.html")
