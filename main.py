from flask import Flask, render_template, request, abort, send_file
from colorama import init
from time import sleep
import json
import os
import sys

app = Flask(__name__)
init()  # Allow Colors on windows based Terminal


def get_list_of_file_depth(dir_path):
    files = {}
    for (dirpath, __, filenames) in os.walk(dir_path):
        for f in filenames:
            static_path = os.path.join(dirpath, f).replace("\\", "/")[1:]
            files.update({f : static_path})

    return files


def get_list_of_file_with_path_surface(dir_path, url_location, default_ftp_location):
    abs_path = os.path.abspath(dir_path)
    file_names = os.listdir(abs_path)
    file_with_path = {}
    for f in file_names:
        if not url_location:
            file_path = "/" + f
        else:
            file_path = "/" + url_location + "/" + f
        file_with_path.update({f : (file_path, os.path.isdir(os.path.abspath("./static/" + default_ftp_location + "/" + file_path)))})
    return file_with_path


@app.route('/', defaults={'path': ''})
@app.route("/<path:path>")
def change_dir(path, default_ftp_location="ftpFiles"):
    try:
        target_path = "./static/" + default_ftp_location + "/" + path
        if os.path.isdir(target_path):
            files = get_list_of_file_with_path_surface(target_path, path, default_ftp_location)
            return render_template("index_no_cata.min.html", 
                                    files=files, 
                                    currentPath=" /" if not path else " /" + path)
        else:
            return send_file(os.path.abspath("./static/" + default_ftp_location + "/" + path), 
                            attachment_filename=path.split("/")[-1], 
                            conditional=True)
    except PermissionError:
        return abort(403)
    except FileNotFoundError:
        return abort(404)


def serve(ipaddr, port):
    app.run(ipaddr, port)


if __name__ == "__main__":
    serve("192.168.29.219", 80)
