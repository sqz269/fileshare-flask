from flask import Flask, render_template, request, abort, send_file, jsonify
from urllib.parse import unquote
from colorama import init
import time
import magic
import os
import platform
import sys

app = Flask(__name__)
init()  # Allow Colors on windows based Terminal

# TODO: WRITE COMMENTS

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def get_list_of_file_depth(dir_path):
    """
    Deprecated

    Get All files from directory and its sub directory

    :Args:
        dir_path (str) A path to a directory to list

    :Return:
        (dict) {"filename": "file relative path"}
    """
    files = {}
    for (dirpath, __, filenames) in os.walk(dir_path):
        for f in filenames:
            static_path = os.path.join(dirpath, f).replace("\\", "/")[1:]
            files.update({f : static_path})

    return files


def get_list_of_file_with_path_surface(dir_path, url_location):
    """
    List all files & directories under a folder. Similar to "ls" in UNIX

    :Args:
        dir_path (str) Path to a directory that is going to be listed
        url_location (str)  A URL location used to point to the file (The file's parent directory's URL path)

    :Return:
        (dict) {<FileName>: (<FilePath>, <IsDirectory>)}
                <FileName> (string);
                <FilePath> (String): URL path to the file;
                <IsDirectory> (Boolean): Is the file a directory;

    :Raise:
        FileNotFoundError when a directory requested for list does not exist
    """
    abs_path = os.path.abspath(dir_path)
    file_names = os.listdir(abs_path)
    file_with_path = {}
    for f in file_names:
        if not url_location:
            file_path = "/" + f
        else:
            file_path = "/" + url_location + f
        file_with_path.update({f : (file_path, os.path.isdir(os.path.abspath("./static/" + app.config["FTPDIR"] + "/" + file_path)))})
    return file_with_path


@app.route("/ShowFileDetail", methods=["POST"])
def get_file_details():
    """
    Get the file properties/metadata from a URL provided for the file
    """
    try:
        file_path_info = request.get_json()  # Posted JSON {"PATH": <URLPath>, "FILENAME": <NameOfTheFile>}
        file_path_browser = file_path_info["PATH"] if file_path_info["PATH"][-1] == "/" else file_path_info["PATH"] + "/"
        #  ^ If PATH provided look like "/blablabla/" then don't add / to the end of it, if it looks like "/blabla" then add "/" to the end to make it "/blabla/"
        file_abs_path = os.path.abspath("./static/" + app.config["FTPDIR"] + "/" + file_path_browser + file_path_info["FILENAME"])

        if "." in file_path_info["FILENAME"]:  # if there is a . in the file name then assume the things behind the . is the file extention
            file_ext = file_path_info["FILENAME"].split(".")[-1]
        else:  # If there is no dot, no file extention
            file_ext = "None"

        file_url_location = file_path_browser + file_path_info["FILENAME"]

        file_info = {
            "file_name": file_path_info["FILENAME"],
            "file_ext": file_ext,
            "file_path": file_path_info["PATH"],
            "last_mod": str(time.ctime(os.path.getmtime(file_abs_path))),  # BUG (Maybe) Modification Date is Earlier than Creation date from some files
            "created": str(time.ctime(creation_date(file_abs_path))),
            "file_size": str(os.path.getsize(file_abs_path)),
            "file_content_type": magic.from_file(file_abs_path).split(",")[0],
            "full_detail": magic.from_file(file_abs_path),
            "location": file_url_location
        }
        return jsonify(file_info)
    except KeyError:  # If path/filename is missing return BAD REQUEST
        abort(400)
    except FileNotFoundError:  # BUG Will raise 404 Even the file exists. but the path have unescaped sequences. for example %20 will cause and file not found
        abort(404)


@app.route('/', defaults={'path': ''}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def change_dir(path):
    """
    List the directory requested from URL
    """
    try:
        target_path = "./static/" + app.config["FTPDIR"] + "/" + path  # Get the relative path for the directory
        if os.path.isdir(target_path):   # If the requested resource is a directory
            files = get_list_of_file_with_path_surface(target_path, path) # Get all file/dir under the requested directory
            if request.method == "GET": # Render webpage if it's GET
                return render_template("index.html",
                                        files=files,
                                        currentPath=" /" if not path else " /" + path)
            elif request.method == "POST": # Else return a JSON
                return jsonify(files)
        else:  # If the requested resource is a file
            # Send the file to clinet
            return send_file(os.path.abspath("./static/" + app.config["FTPDIR"] + "/" + path),
                            attachment_filename=path.split("/")[-1],
                            conditional=True) # Conditional True makes it transfer using STATUS 206 (Chunk by chunk) 
    except PermissionError:
        return abort(403)
    except FileNotFoundError:
        return abort(404)


def serve(ipaddr, port, ftpDir="ftpFiles", debug=False):
    """
    Start the server

    :Args:
        ipaddr (str) IP address the server should bind to
        port (int)  Port number the server should listening at
        ftpDir (str)  Where will be the shared file stored (MUST be under ./static)
        debug (Bool)  Debug Mode
    """
    app.config.update({"FTPDIR": ftpDir})
    app.run(ipaddr, port)


if __name__ == "__main__":
    # ARGUMENT 1: IP Address, 2: Port
    serve("localhost", 80)
