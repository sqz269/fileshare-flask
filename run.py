from fileshare import app
from fileshare.shared.database.database import db
from fileshare.shared.database.init import init_db

# DEBUG    10
# INFO     20
# WARNING  30
# ERROR    40
# CRITICAL 50
app.logger.setLevel(10)

if __name__ == "__main__":
    app.config.from_object("config_local.ConfigTesting")
else:
    app.config.from_object("config_local.ConfigProduction")

db.init_app(app)
init_db()

if __name__ == "__main__":
    app.run(app.config["LOCAL_BINDING_IP_ADDRESS"], app.config["LOCAL_BINDING_PORT"])
