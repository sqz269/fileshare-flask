from flask import Flask

app = Flask(__name__)

from fileshare.site.views import site
from fileshare.api.views import api

app.register_blueprint(site)
app.register_blueprint(api)
