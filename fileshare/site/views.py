from flask import Blueprint, render_template, request, send_file, abort
from flask import current_app as app

from fileshare.shared.libs.paths import make_abs_path_from_url
from fileshare.shared.libs.utils import get_url_param

from fileshare.shared.database.common_query import CommonQuery

import time
import os

import magic

site = Blueprint("site", __name__, template_folder="template", static_folder="static", static_url_path="/site/static")

mime = magic.Magic(True)

@site.route('/', methods=["GET"])
def filepage():
    if app.config["ACCESS_PASSWORD"]:
        # CHECK FOR ACCESS TOKEN
        pass
    else:
        return render_template("index.html")


@site.route("/<path:path>", methods=["GET"])
def files(path):
    print("Access path: {}".format(path))
    try:
        mode_download = get_url_param(request.args, "mode") == "download"

        path = "/" + path # Add the pre fix / to the path, cuz all the rel path have a / in the beginning

        if os.name == "nt":
            path = path.replace("/", "\\")

        file = CommonQuery.query_file_by_relative_path(path)

        if not file:
            return render_template("error/404.html")

        if mode_download:
            return send_file(file.abs_path, True, file.name)
        else:
            return send_file(file.abs_path, mimetype=file.mimetype, attachment_filename=file.name)

    except (PermissionError, FileNotFoundError):
        return render_template("error/404.html")
