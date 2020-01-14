from flask import Flask

app = Flask(__name__)

from fileshare.site.views import site
from fileshare.api.views import api

from fileshare.api_admin.views import api_admin
from fileshare.site_admin.views import site_admin

app.register_blueprint(site)
app.register_blueprint(api)

app.register_blueprint(site_admin)
app.register_blueprint(api_admin)
