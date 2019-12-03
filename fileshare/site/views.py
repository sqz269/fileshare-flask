from flask import Blueprint, render_template, request, send_from_directory
from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs.utils import is_access_token_valid, get_url_param, is_access_token_valid_no_path
from fileshare.api.libs.paths import make_abs_path_from_url

import magic

site = Blueprint("site", __name__, template_folder="templates", static_folder="static", static_url_path="/site/static")


configuration = ConfigurationMgr()

mime = magic.Magic(mime=True)

@site.route('/', methods=["GET"])
def homepage():
    if configuration.config.get("ACCESS_PASSWORD"):
        if is_access_token_valid_no_path(request.cookies, request.args):
            return render_template("index.html")
        else:
            return render_template("password.html")
    else:
        return render_template("index.html")


# Request a file to serve, url paramater "mode" is avaliable
# only value mode can be is "download" which force to send the file as an attachment
# which the browser will proceed to download that file
@site.route('/<path:path>', methods=["GET"])
def files(path):
    try:

        is_mode_download = get_url_param(request.args, "mode") == "download"

        if configuration.config.get("DETECT_FILE_MIME"):
            # If the user want us to automatically determin the mime type of the file
            # we can serve stuff like img/vid directly instead of having to download
            abs_path = make_abs_path_from_url(path, configuration.config.get("SHARED_DIR"))

            # Sometime libmagic fails with unicode file names, then we have to open them and pass it to read_buffer
            # https://stackoverflow.com/questions/34836792/python-magic-cant-identify-unicode-filename

            # f_mime = mime.from_file(abs_path)
            with open(abs_path, "rb") as file:
                f_mime = mime.from_buffer(file.read(1024))

            print("Detected mime type for file: {} | type: {}".format(path, f_mime)) # TODO DO NOT detect mime type if it is streaming

        if configuration.config.get("FILE_MIME"):
            f_mime = configuration.config.get("FILE_MIME")

        if is_access_token_valid(request.cookies, request.args, path):
            if is_mode_download:
                return send_from_directory(configuration.config.get("SHARED_DIR"), path, as_attachment=True)
            else:
                return send_from_directory(configuration.config.get("SHARED_DIR"), path, mimetype=f_mime)
        else:
            return render_template("password.html")

        if is_mode_download:
            return send_from_directory(configuration.config.get("SHARED_DIR"), path, as_attachment=True)
        else:
            return send_from_directory(configuration.config.get("SHARED_DIR"), path, mimetype=f_mime)
    except (PermissionError, FileNotFoundError):
        return render_template("error/404.html")
