from flask import Flask, render_template, request, abort, send_file, json
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from urllib.parse import unquote
from base64 import b64encode
from colorama import init
from shutil import rmtree
import configparser
import jwt
import time
import magic
import os


def load_config_from_file():
    cfg = configparser.ConfigParser()
    cfg.read("server-config.ini")
    server_cfg = cfg["SERVER"]
    db_uri = server_cfg.get("DATABASE_URI")
    secret_key = server_cfg.get("SECRET_KEY")
    file_dir = server_cfg.get("FILEDIR")
    use_secure_filename = server_cfg.getboolean("SECURE_UPLOAD_FILENAME")
    upload_auth_required = server_cfg.getboolean("UPLOAD_AUTH_REQUIRED")
    delete_auth_required = server_cfg.getboolean("DELETE_AUTH_REQUIRED")
    mkdir_auth_required = server_cfg.getboolean("MKDIR_AUTH_REQUIRED")
    jwt_valid_time = int(server_cfg.get("JWT_VALID_FOR"))
    config(db_uri,
        secret_key,
        file_dir,
        JWT_valid_time=jwt_valid_time, 
        secure_upload_filename=use_secure_filename, 
        upload_auth_required=upload_auth_required,
        delete_auth_required=delete_auth_required)


def config(database_uri, secret_key, fileDir, JWT_valid_time=86400, secure_upload_filename=True, upload_auth_required=True, delete_auth_required=True, mkdir_auth_required=True):
    """
    Config the server

    :Args:
        database_path (str) uri points to the database to store user login credentials
        secret_key (str) key will be used to encrypt the server's JWT, will be encoded to utf-8
        fileDir (str)  Where will be the shared file stored (MUST be under ./static)
    """
    init()  # Allow Colors on windows Terminal (cmd/powershell)
    app.logger.critical(database_uri)
    app.config.update({"SQLALCHEMY_DATABASE_URI": database_uri})
    app.config.update({"SECRET_KEY": secret_key.encode("utf-8")})
    app.config.update({"FILEDIR": fileDir})
    app.config.update({"SECUREFILENAME": secure_upload_filename})
    app.config.update({"UPLOAD_AUTH_REQUIRED": upload_auth_required})
    app.config.update({"DELETE_AUTH_REQUIRED": delete_auth_required})
    app.config.update({"MKDIR_AUTH_REQUIRED": mkdir_auth_required})
    app.config.update({"JWT_VALID_FOR": JWT_valid_time})
    if not secure_upload_filename:
        app.logger.warning("SECURE UPLOAD FILE NAME IS DISABLED. THIS MIGHT CAUSE UNEXPECTED CONSEQUENCES")
    app.logger.debug(app.config.get("SECRET_KEY"))


app = Flask(__name__)

load_config_from_file()

bcrypt = Bcrypt(app=app)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<ID %r; User %r;>' % (self.id, self.username)

    def get_user_password(self):
        return self.password


def database_add_user(username, password_plain_text):
    """
    Add a new user to the database

    :Args:
        username (str) The user's username
        password_plain_text (str) The user's password that is in plain text form (will be encrypted using bCrypt before adding to database)
    """
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
    try:
        return bcrypt.check_password_hash(record.get_user_password(), password_plain_text)
    except:
        return False


def make_json_resp_with_status(json_data, http_status):
    """
    Return JSON Response with a valid HTTP Status code

    :Args:
        json_data (dict) Json that will be send 
        http_status (int) HTTP status code that will be included in the response

    :Return:
        Flask response_class object (with mimetype: application/json)
    """
    response = app.response_class(response=json.dumps(json_data),
                                status=http_status,
                                mimetype='application/json')
    return response


def JWT_validate(encoded_jwt, remote_addr):
    """
    Check if a Json Web Token (Used to store login sessions) is valid

    :Args:
        encoded_jwt (str) the json web token encoded (send from the client)
        remote_addr (str) the ip address of the client

    :Return:
        (bool) True if the web token is valid else return false
    """
    try:
        jwt_decoded = jwt.decode(encoded_jwt, app.config["SECRET_KEY"])
        created = jwt_decoded["CREATED"]
        valid = jwt_decoded["VALIDFOR"]
        issuedfor = jwt_decoded["ISSUEDFOR"]
        return (time.time() < created + valid) and (issuedfor == remote_addr)
    except jwt.exceptions.InvalidSignatureError:
        return False


def JWT_issue(ipaddr):
    """
    Generate a Json Web Token to indicate login sessions
        Includes Creation date, Validation Time, Client Address
        Token Encoded with "SECRET_KEY" as key

    :Args:
        ipaddr (str) Client's ip address

    :Return:
        (str) Json web token
    """
    return jwt.encode({"CREATED": time.time(), "VALIDFOR": app.config["JWT_VALID_FOR"], "ISSUEDFOR": ipaddr}, app.config["SECRET_KEY"])


def make_abs_path_from_url(uri):
    """
    Make abslute path from requested URI

    :Args:
        uri (str) uri the user requested

    :Return:
        (str) the abs path made from the uri that points to the file/dir the user requested 
    """
    return app.config["FILEDIR"] + uri if uri[0] == "/" or uri[0] == "\\" else app.config["FILEDIR"] + "/" + uri


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if os.name == 'nt':  # If the os running on is windowsNT
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
        (dict) {<FileName>: (<FilePath>, <IsDirectory>)};
                <FileName> : (string) File name
                <FilePath> : (String) URL path to the file;
                <IsDirectory> : (Boolean) Is the file a directory;

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
        file_with_path.update({f : (file_path, os.path.isdir(os.path.abspath(app.config["FILEDIR"] + "/" + file_path)))})
    return file_with_path


@app.route("/Login", methods=["POST"])
def auth():
    try:
        login_data = request.get_json()
        if not login_data["USERNAME"] or not login_data["PASSWORD"]:
            return make_json_resp_with_status({"STATUS" : 1, "Details": "Invalid username or password"}, 401)

        isAuthSuccess = database_user_auth(login_data["USERNAME"], login_data["PASSWORD"])
        if isAuthSuccess:
            resp = make_json_resp_with_status({"STATUS": 0, "Details": "Authorized"}, 200)
            resp.set_cookie("AUTH_TOKEN", JWT_issue(request.remote_addr))
            return resp
        else:
            return make_json_resp_with_status({"STATUS" : 1, "Details": "Invalid username or password"}, 401)
    except Exception as err:
        print(err)
        return make_json_resp_with_status({"STATUS": 3, "Details": "Unable to proceed to authorize. Exception occurred: {}".format(err)}, 500)


@app.route("/Move", methods=["POST"])
def move_file():
    return make_json_resp_with_status({"STATUS": 1337, "Details": "Feature Working In Progress"}, 501)


@app.route("/GetDirectories", methods=["POST"])
def get_all_dirs():
    dirs = next(os.walk('.'))[1]
    list_of_dir = {"DIRS": dirs}
    return make_json_resp_with_status(list_of_dir, 200)

@app.route("/Mkdir", methods=["POST"])
def make_dir():
    if app.config["MKDIR_AUTH_REQUIRED"]:
        try:
            jwt_token = request.cookies["AUTH_TOKEN"]
        except KeyError as noToken:
            return make_json_resp_with_status({"STATUS": 5,"Details": "Unable to create directory, Authentication required."}, 401)

        if not JWT_validate(jwt_token, request.remote_addr):
            return make_json_resp_with_status({"STATUS": 5,"Details": "Unable to create directory, Authentication required."}, 401)


    try:
        # DIR JSON: {"DIR": ["/asdsf", "/ifasd", "/asdsf/asdfasdf"]}
        dirs = request.get_json()
        dir_list = dirs.get("DIR")
        
        for directories in dir_list:
            dir_abs_path = make_abs_path_from_url(directories)
            os.mkdir(dir_abs_path)

        return make_json_resp_with_status({"STATUS": 0, "Details": "Success"}, 200)

    except PermissionError:
        return make_json_resp_with_status({"STATUS": 1, "Details": "Unable to create directory, Access to resource is denied by OS"}, 403)
    except FileExistsError:
        return make_json_resp_with_status({"STATUS": 3, "Details": "Unable to create directory, Directory already exist"}, 400)
    except Exception as error:
        return make_json_resp_with_status({"STATUS": 3, "Details": "Unable to create directory, An Exception occurred: {}".format(error)}, 500)



@app.route("/Delete", methods=["DELETE", "POST"])
def delete_file():
    file_list = request.get_json()  # Posted JSON {"FILES": [ListOfFiles]}
    
    if app.config["DELETE_AUTH_REQUIRED"]:

        try:
            jwt_token = request.cookies["AUTH_TOKEN"]
        except KeyError as noToken:
            return make_json_resp_with_status({"STATUS": 5,"Details": "Unable to delete file, Authentication required."}, 401)

        if not JWT_validate(jwt_token, request.remote_addr):
            return make_json_resp_with_status({"STATUS": 5,"Details": "Unable to delete file, Authentication required."}, 401)

    try:
        file_list = file_list.get("FILES")
        for file in file_list:
            file_abs_path = make_abs_path_from_url(file)
            app.logger.critical("Attempting to delete: {}".format(file_abs_path))
            if os.path.isdir(file_abs_path):
                rmtree(file_abs_path)
            else:
                os.remove(file_abs_path)
        return make_json_resp_with_status({"STATUS": 0, "Details": "Success"}, 200)
    except PermissionError:
        return make_json_resp_with_status({"STATUS": 1, "Details": "Unable to delete file, Access to resource is denied by OS"}, 403)
    except FileNotFoundError:
        return make_json_resp_with_status({"STATUS": 2, "Details": "Unable to delete file, Target file does not exist"}, 404)
    except Exception as error:
        return make_json_resp_with_status({"STATUS": 3, "Details": "Unable to delete file, An Exception occurred: {}".format(error)}, 500)


@app.route("/Upload", methods=["POST"])
def upload_file():
    # check if the post request has the file part
    if app.config["UPLOAD_AUTH_REQUIRED"]:
        try:
            jwt_token = request.cookies["AUTH_TOKEN"]
        except KeyError as noToken:
            return make_json_resp_with_status({"STATUS": 5,"Details": "Upload Aborted, Authentication required."}, 401)

        if not JWT_validate(jwt_token, request.remote_addr):
            return make_json_resp_with_status({"STATUS": 5,"Details": "Upload Aborted, Authentication required."}, 401)

    try:
        dst_dir = request.args.get("dst")
    except:
        return make_json_resp_with_status({"STATUS": 2, "Details": "Unable to upload file, Desnation not specified"}, 400)

    dir_abs_path = make_abs_path_from_url(dst_dir)

    files = request.files.getlist("File")
    for file in files:
        if not app.config["SECUREFILENAME"]:
            file_name = file.filename
        else:
            file_name = secure_filename(file.filename)
        dst_abs_path = dir_abs_path + file_name
        file.save(dst_abs_path)

    return make_json_resp_with_status({"STATUS": 0, "Details": "File uploaded successfully"}, 200)


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
        file_abs_path = os.path.abspath(app.config["FILEDIR"] + "/" + file_path_browser + file_path_info["FILENAME"])
        if "." in file_path_info["FILENAME"]:  # if there is a . in the file name then assume the things behind the . is the file extention
            file_ext = file_path_info["FILENAME"].split(".")[-1]
        else:  # If there is no dot, no file extention
            file_ext = "None"

        file_url_location = file_path_browser + file_path_info["FILENAME"]

        file_info = {
            "file_name": file_path_info["FILENAME"],
            "file_ext": file_ext,
            "file_path": file_path_info["PATH"],
            "last_mod": str(time.ctime(os.path.getmtime(file_abs_path))),
            "created": str(time.ctime(creation_date(file_abs_path))),
            "file_size": str(os.path.getsize(file_abs_path)),
            "file_content_type": magic.from_file(file_abs_path).split(",")[0],
            "full_detail": magic.from_file(file_abs_path),
            "location": file_url_location
        }
        return make_json_resp_with_status(file_info, 200)
    except KeyError:  # If path/filename is missing return BAD REQUEST
        abort(400)
    except FileNotFoundError:
        abort(404)


@app.route('/', defaults={'path': ''}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def change_dir(path):
    """
    List the directory requested from URL
    """
    try:
        target_path = app.config["FILEDIR"] + "/" + path  # Get the relative path for the directory
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
            return send_file(os.path.abspath(app.config["FILEDIR"] + "/" + path),
                            attachment_filename=path.split("/")[-1],
                            conditional=True) # Conditional True makes it transfer using STATUS 206 (Chunk by chunk)
    except PermissionError:
        return make_json_resp_with_status({"STATUS": 1, "Details": "Unable to get files, Access to resource is denied by OS"}, 403)
    except FileNotFoundError:
        return make_json_resp_with_status({"STATUS": 2, "Details": "Unable to get files, Target directory/file does not exist"}, 404)


def serve(ipaddr, port, debug=False):
    """
    Start the server

    :Args:
        ipaddr (str) IP address the server should bind to
        port (int)  Port number the server should listening at
    """
    app.run(ipaddr, port, debug=debug)


if __name__ == "__main__":
    serve("localhost", 80, debug=True)
