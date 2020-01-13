class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///D:/PROG/fileshare-flask-refactor/test.db"
    SHARED_DIRECTORY = ["E:\\GeneralWebsite\\ftpFiles"]
    # List of directory to be shared, use absolute path

    SECURE_UPLOAD_FILENAME = True
    # bool, True werkzeug.secure_filename will be called on the uploaded file name
    # It is strongly advised to set this option to true as it's only way to prevent malicious path names being used

    DATABASE_URI = None

    DETECT_FILE_MIME = True
    # True if you want the program to use "magic.Magic(mime=True).from_buffer()" to detect the file's mime type and serve accordingly
    FILE_MIME = None
    #  Force to serve all files using this mime type, will override detect_file_mime

    ACCESS_PASSWORD = None
    #  if you don't want a password then leave it as a false value

    DELETE_MODE = 2
    # delete mode represents how is a file going to be deleted
    # 1 Represents the file/folder's record is only going to be deleted from the database, not the filesystem
    # 2 represents both the database record and the actual file is going to be removed 

    ALLOW_ACCESS_TOKEN_AS_URL_PARAM = False
    #  bool, True if user can provide their AccessTokens (JWT) as a url paramater, useful for temporary access sharing 

    ALLOW_USER_ISSUE_TOKEN = False
    #  bool, True if a user that is authorized can issue a AccessToken for sharing files/dir to other non authorized users
    #  This option requires allow_access_token_as_url_param to be true

    SHARE_FILE_AUTH_REQUIRED = False
    #  bool, cooprates with (allow_access_token_as_url_param, allow_user_issue_token)
    #  Only will be in effect if (allow_access_token_as_url_param, allow_user_issue_token) are true
    #  Only allows user who are logged in to issue a access token


    UPLOAD_AUTH_REQUIRED = True
    #  bool, True if login is required to upload a file
    MKDIR_AUTH_REQUIRED = True
    #  bool, True if login is required to make a new folder
    DELETE_AUTH_REQUIRED = True
    #  bool, True if login is required to delete a file/folder
    RENAME_AUTH_REQUIRED = True
    #  bool, True if login is required to rename a file/folder


class ConfigTesting(Config):
    pass


class ConfigProduction(Config):
    pass
