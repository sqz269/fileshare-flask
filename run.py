from fileshare import app

from fileshare.shared.database.database import db

from fileshare.shared.database.init import init_db

# prepare_db()

if __name__ != "__main__":
    app.config.from_object("config_local.ConfigProduction")
else:
    app.config.from_object("config_local.ConfigTesting")

db.init_app(app)

init_db()

if __name__ == "__main__":
    app.run("localhost", 5000)
