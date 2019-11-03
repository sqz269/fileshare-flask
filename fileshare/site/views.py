from flask import Blueprint, render_template


site = Blueprint("site", __name__, template_folder="templates", static_folder="static", static_url_path="/site/static")

@site.route("/")
def homepage():
    return render_template("index.html")
