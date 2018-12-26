from flask import Flask, render_template, request, abort, send_file, jsonify
from colorama import init
import time
import magic
import os
import sys

app = Flask(__name__)
init()  # Allow Colors on windows based Terminal

# TODO: WRITE COMMENTS

def get_list_of_file_depth(dir_path):
    files = {}
    for (dirpath, __, filenames) in os.walk(dir_path):
        for f in filenames:
            static_path = os.path.join(dirpath, f).replace("\\", "/")[1:]
            files.update({f : static_path})

    return files


def get_list_of_file_with_path_surface(dir_path, url_location):
    abs_path = os.path.abspath(dir_path)
    file_names = os.listdir(abs_path)
    file_with_path = {}
    for f in file_names:
        if not url_location:
            file_path = "/" + f
        else:
            file_path = "/" + url_location + "/" + f
        file_with_path.update({f : (file_path, os.path.isdir(os.path.abspath("./static/" + app.config["FTPDIR"] + "/" + file_path)))})
    return file_with_path


@app.route("/ShowFileDetail", methods=["POST"])
def get_file_details():
    try:
        file_path_info = request.get_json()
        file_path_browser = file_path_info["PATH"] if file_path_info["PATH"][-1] == "/" else file_path_info["PATH"] + "/"
        file_abs_path = os.path.abspath("./static/" + app.config["FTPDIR"] + "/" + file_path_browser + file_path_info["FILENAME"])
        if file_path_info["FILENAME"].count("."):
            file_ext = file_path_info["FILENAME"].split(".")[-1]
        else:
            file_ext = "None"
        if file_path_info["PATH"] == "/":
            file_url_location = file_path_info["PATH"] + file_path_info["FILENAME"]
        else:
            file_url_location = file_path_info["PATH"] + "/" + file_path_info["FILENAME"]
        file_info = {
            "file_name": file_path_info["FILENAME"],
            "file_ext": file_ext,
            "file_path": file_path_info["PATH"],
            "last_mod": str(time.ctime(os.path.getmtime(file_abs_path))),
            "created": str(time.ctime(os.path.getctime(file_abs_path))),
            "file_size": str(os.path.getsize(file_abs_path)),
            "file_type": magic.from_file(file_abs_path).split(",")[0],
            "full_detail": magic.from_file(file_abs_path),
            "location": file_url_location
        }
        return jsonify(file_info)
    except KeyError:  # If path/filename is missing return BAD REQUEST
        abort(400)
    except FileNotFoundError:
        abort(404)


@app.route('/', defaults={'path': ''})
@app.route("/<path:path>")
def change_dir(path):
    try:
        target_path = "./static/" + app.config["FTPDIR"] + "/" + path
        if os.path.isdir(target_path):
            files = get_list_of_file_with_path_surface(target_path, path)
            return render_template("index.html", 
                                    files=files, 
                                    currentPath=" /" if not path else " /" + path)
        else:
            return send_file(os.path.abspath("./static/" + app.config["FTPDIR"] + "/" + path), 
                            attachment_filename=path.split("/")[-1], 
                            conditional=True)
    except PermissionError:
        return abort(403)
    except FileNotFoundError:
        return abort(404)


def serve(ipaddr, port, ftpDir="ftpFiles", debug=False):
    app.config.update({"FTPDIR": ftpDir})
    app.run(ipaddr, port)


if __name__ == "__main__":
    # ARGUMENT 1: IP Address, 2: Port
    serve("192.168.29.219", 80)
