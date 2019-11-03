from flask import Flask

app = Flask(__name__)

from fileshare.api.views import api
from fileshare.site.views import site

app.register_blueprint(api)
app.register_blueprint(site)
