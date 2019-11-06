from fileshare import app
from fileshare.libs.configurationMgr import ConfigurationMgr

initCfg = ConfigurationMgr().read_config("config_local.ini")

if __name__ == "__main__":
    app.run("localhost", 3000, debug=True)
