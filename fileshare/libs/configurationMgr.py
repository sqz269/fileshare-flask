import configparser
from fileshare.libs.utils import Singleton
from fileshare.libs.logger import init_logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

class ConfigurationMgr(object, metaclass=Singleton):


    def __init__(self):
        self.config = {
            "SHARED_DIR": None,
            "DATABASE_URI": None,
            "SECURE_UPLOAD_FILENAME": None,

            "JWT_SECRET_KEY": None,
            "JWT_VALID_FOR": None,  # Seconds

            "ACCESS_PASSWORD": None,

            "UPLOAD_AUTH_REQUIRED": None,
            "DELETE_AUTH_REQUIRED": None,
            "MKDIR_AUTH_REQUIRED": None,
            "RENAME_AUTH_REQUIRED": None,
        }

        self.str_to_logging_lvl = {
            "DEBUG": DEBUG,
            "INFO": INFO,
            "WARNING": WARNING,
            "ERROR": ERROR,
            "CRITICAL": CRITICAL
        }

        self.logger_name = None


    def read_config(self, path):
        cfg = configparser.ConfigParser()
        cfg.read(path)

        cfg_general = cfg["General"]
        cfg_permission = cfg["Permission"]
        cfg_jwt = cfg["JWT"]
        cfg_logging = cfg["Logging"]

        self.logger_name = cfg_logging["logger_name"]
        logging_level_out = self.str_to_logging_lvl.get(cfg_logging["level_stdout"].upper())
        logging_level_file = self.str_to_logging_lvl.get(cfg_logging["level_file"].upper())

        init_logging(logging_level_out,logging_level_file, self.logger_name)

        self.config["SHARED_DIR"] = cfg_general["shared_directory"]
        self.config["SECURE_UPLOAD_FILENAME"] = cfg_general["secure_upload_filename"]
        self.config["DATABASE_URI"] = cfg_general["database_uri"]

        self.config["JWT_SECRET_KEY"] = cfg_jwt["JWT_key"]
        self.config["JWT_VALID_FOR"] = cfg_jwt["JWT_valid_for"]

        self.config["UPLOAD_AUTH_REQUIRED"] = cfg_permission["upload_auth_required"]
        self.config["DELETE_AUTH_REQUIRED"] = cfg_permission["delete_auth_required"]
        self.config["RENAME_AUTH_REQUIRED"] = cfg_permission["rename_auth_required"]
        self.config["MKDIR_AUTH_REQUIRED"] = cfg_permission["mkdir_auth_required"]
        
        self.config["ACCESS_PASSWORD"] = cfg_permission["access_password"]