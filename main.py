from flask import Flask, render_template, request, abort, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from urllib.parse import unquote
from base64 import b64encode
from colorama import init
import jwt
import time
import magic
import os
import platform

# Path operations possibly contains vulnerability

app = Flask(__name__)
bcrypt = Bcrypt(app=app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # last_login_date = db.Column(db.String(40), nullable=True)
    # last_login_addr = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return '<ID %r; User %r;>' % (self.id, self.username)

    def get_user_password(self):
        return self.password

    # def get_user_last_login_date(self):
    #     return self.last_login_date

    # def get_user_last_login_addr(self):
    #     return self.last_login_addr


def database_add_user(username, password_plain_text):
    user = User(username=username, password=bcrypt.generate_password_hash(password_plain_text.encode("utf-8")))
    db.session.add(user)
    db.session.commit()


def database_delete_user(username):
    """
    Delete user from database

    :Args:
        username (str) the user's username to be deleted from the db
    """
    User.query.filter(User.username == username).delete()
    db.session.commit()


def database_user_auth(username, password_plain_text):
    """
    Check if the user have the correct credentials to login

    :Args:
        username (str) the username to login
        password (str) the password

    :Return:
        (bool) True if the user's credential is valid, else return False
    """
    record = User.query.filter(User.username == username).first()
    print("Plain Text: {}\nEncoded: {}".format(password_plain_text,record.get_user_password()))
    return bcrypt.check_password_hash(record.get_user_password(), password_plain_text)


def database_test():
    db.drop_all()
    db.create_all()
    database_add_user("admin", "hunter2")
    # user = User(username="administrator", password="hunter2")
    # user_0 = User(username="admin", password="hunter2")
    # user_1 = User(username="anon", password="fag")
    # db.session.add(user_0)
    # db.session.commit()

    # User.query.filter(User.username == "anon").delete()
    # db.session.commit()

    # data = User.query.all()
    # print(data)

    # record = User.query.filter(User.username == "admin").first()
    # print(record)
    # print(record.get_user_password())

    # database_delete_user("notauser")


# database_test()


def JWT_validate(encoded_jwt):
    jwt_decoded = jwt.decode(encoded_jwt, app.config["SECRET_KEY"])
    created = jwt_decoded["CREATED"]
    valid = jwt_decoded["VALIDFOR"]
    print("IS JWT VALID: {}".format(time.time() < created + valid))
    return time.time() < created + valid


def JWT_issue(valid_time=86400):
    return jwt.encode({"CREATED": time.time(), "VALIDFOR": valid_time}, app.config["SECRET_KEY"])


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
        file_with_path.update({f : (file_path, os.path.isdir(os.path.abspath("./static/" + app.config["FILEDIR"] + "/" + file_path)))})
    return file_with_path


@app.route("/Login", methods=["POST"])
def auth():
    login_data = request.get_json()

    if not login_data["USERNAME"] or not login_data["PASSWORD"]:
        return jsonify({"STATUS" : 1, "Details": "Invalid username or password"})

    print(login_data)
    isAuthSuccess = database_user_auth(login_data["USERNAME"], login_data["PASSWORD"])
    if isAuthSuccess:
        data = jsonify({"STATUS" : 0, "Details": "Authorized"})
        data.set_cookie("AUTH_TOKEN", JWT_issue())
        return data
    else:
        return jsonify({"STATUS" : 1, "Details": "Invalid username or password"})


@app.route("/Move", methods=["POST"])
def move_file():
    pass


@app.route("/Upload", methods=["POST"])  # RESTFUL
def upload_file():
    # check if the post request has the file part
    if app.config["UPLOAD_AUTH_REQUIRED"]:
        try:
            jwt_token = request.cookies["AUTH_TOKEN"]
        except KeyError as noToken:
            abort(401)

        if not JWT_validate(jwt_token):
            abort(401)

    dst_dir = request.args.get("dst")

    if not dst_dir:
        return jsonify({"STATUS": 1, "Details": "Destination is not specified"})

    dst_dir_abs_path = os.path.abspath("./static/" + app.config["FILEDIR"] + "/" + dst_dir)
    if dst_dir_abs_path[-1] != "/" or dst_dir_abs_path[-1] != "\\":
        dst_dir_abs_path += "/"

    files = request.files.getlist("File")
    for file in files:
        if not app.config["SECUREFILENAME"]:
            file_name = file.filename
        else:
            file_name = secure_filename(file.filename)
        print(dst_dir_abs_path)
        dst_abs_path = dst_dir_abs_path + file_name
        file.save(dst_abs_path)
    print("File Uploaded: {}".format(files))
    return jsonify({"STATUS": 0, "Details": "File uploaded successfully"})


@app.route("/Delete", methods=["DELETE"])
def delete_file():
    file_path = request.get_json()  # Posted JSON {"PATH": <FileURL>}
    # TODO Check user Privilege return 403 (int) (Json) If no privilege to delete else return 0 (int) json form
    try:
        os.remove(os.path.abspath(file_path))
        return jsonify({"STATUS": 0, "Details": "Success"})
    except PermissionError:
        return jsonify({"STATUS": 1, "Details": "Unable to delete file, Access denied"})
    except FileNotFoundError:
        return jsonify({"STATUS": 2, "Details": "Unable to delete file, Target file does not exist"})
    except Exception as error:
        return jsonify({"STATUS": 3, "Details": "Unable to delete file, An Exception occurred: {}".format(error)})


@app.route("/ShowFileDetail", methods=["POST"])
def get_file_details():
    """
    Get the file properties/metadata from a URL provided for the file
    """
    try:
        file_path_info = request.get_json()  # Posted JSON {"PATH": <URLPath>, "FILENAME": <NameOfTheFile>}
        file_path_info["PATH"] = unquote(file_path_info["PATH"])  # Unescape URL sequence to normal characters
        file_path_browser = file_path_info["PATH"] if file_path_info["PATH"][-1] == "/" else file_path_info["PATH"] + "/"
        #  ^ If PATH provided look like "/blablabla/" then don't add / to the end of it, if it looks like "/blabla" then add "/" to the end to make it "/blabla/"
        file_abs_path = os.path.abspath("./static/" + app.config["FILEDIR"] + "/" + file_path_browser + file_path_info["FILENAME"])
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
        target_path = "./static/" + app.config["FILEDIR"] + "/" + path  # Get the relative path for the directory
        if os.path.isdir(target_path):   # If the requested resource is a directory
            files = get_list_of_file_with_path_surface(target_path, path) # Get all file/dir under the requested directory
            if request.method == "GET": # Render webpage if it's GET
                return render_template("index.html",
                                        files=files,
                                        currentPath=" /" if not path else " /" + path)
            elif request.method == "POST": # Else return a JSON
                return jsonify(files)
        else:  # If the requested resource is a file
            # Send the file to client
            return send_file(os.path.abspath("./static/" + app.config["FILEDIR"] + "/" + path),
                            attachment_filename=path.split("/")[-1],
                            conditional=True) # Conditional True makes it transfer using STATUS 206 (Chunk by chunk)
    except PermissionError:
        return abort(403)
    except FileNotFoundError:
        return abort(404)


def config(database_uri, secret_key, fileDir="ftpFiles", secure_upload_filename=True, upload_auth_required=True):
    """
    Config the server

    :Args:
        database_path (str) uri points to the database to store user login credentials
        secret_key (str) key will be used to encrypt the server's JWT, will be encoded to utf-8
        ftpDir (str)  Where will be the shared file stored (MUST be under ./static)
    """
    init()  # Allow Colors on windows Terminal (cmd/powershell)
    app.config.update({"SQLALCHEMY_DATABASE_URI": database_uri})
    # b64encode(os.urandom(15))
    # WARNING: CHANGE THE SECRET KEY TO YOUR OWN
    app.config.update({"SECRET_KEY": secret_key.encode("utf-8")})

    app.config.update({"FILEDIR": fileDir})
    app.config.update({"SECUREFILENAME": secure_upload_filename})
    app.config.update({"UPLOAD_AUTH_REQUIRED": upload_auth_required})
    if not secure_upload_filename:
        app.logger.warning("SECURE UPLOAD FILE NAME IS DISABLED. THIS MIGHT CAUSE UNEXPECTED CONSEQUENCES")
    app.logger.debug(app.config.get("SECRET_KEY"))


def serve(ipaddr, port, debug=False):
    """
    Start the server

    :Args:
        ipaddr (str) IP address the server should bind to
        port (int)  Port number the server should listening at
    """
    app.run(ipaddr, port, debug=debug)

config("", "")  # Arg1: DB URI, Arg2: Secret Key

if __name__ == "__main__":
    serve("localhost", 80, debug=True)
