from fileshare import app
from fileshare.libs.configurationMgr import ConfigurationMgr

initCfg = ConfigurationMgr().read_config("config.ini")

app.run("localhost", 3000, debug=True)
