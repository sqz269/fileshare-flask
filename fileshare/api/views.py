from flask import Blueprint

from fileshare.libs.configurationMgr import ConfigurationMgr

cfg = ConfigurationMgr()

api = Blueprint("api", __name__, url_prefix="/api/files")

@api.route("/test")
def test():
    return "THIS IS A TEST"
