from flask import Blueprint, render_template, request, send_from_directory
from fileshare.libs.configurationMgr import ConfigurationMgr
from fileshare.api.libs.utils import make_json_resp_with_status, get_url_param

api_admin = Blueprint("api_admin", __name__, url_prefix="/api/admin")

# @api_admin.route("top_files")
# def top_files():
#     pass

configuration = ConfigurationMgr()

"""
Admin panel specific error codes
50 - Invalid fields provided (this can be type mismatch or key to access to an non-existent resources) | 400

"""


@api_admin.route("/configuration/all", methods=["GET"])
def get_all_configurations():
    return make_json_resp_with_status({"status": 0, "details": "completed", "results": configuration.config}, 200)


@api_admin.route("/configuration/<string:key>", methods=["GET"])
def get_configuration(key):
    try:
        return make_json_resp_with_status({"status": 0, "details": "completed", "results": [configuration.config[key]]}, 200)
    except:
        return make_json_resp_with_status({"status": 50, "details": f"no configurations is associated with key: {key}. note: most configuration keys are all caps letters", "results": []}, 400)


@api_admin.route("/configuration/<string:key>", methods=["POST"])
def update_configuration(key):
    try:
        value = get_url_param(request.args, "value")
        target_type = get_url_param(request.args, "type")

        old_value = configuration.config[key]
        value = type(configuration.config[key])(value)
        configuration.config[key] = value
        return make_json_resp_with_status({"status": 0,
                                            "details": f"configuration: {key} with old value {old_value} -> {value}",
                                            "results": []},
                                            200)

    except KeyError:
        return make_json_resp_with_status({"status": 50,
                                           "details": f"no configuration associated with such key: {key}. note: most configuration keys are all caps letters",
                                           "results": []},
                                           200)
    except ValueError:
        return make_json_resp_with_status({"status": 50, 
                                           "details": f"type mismatch, field: {key} requires type: {type(key)}, but provided value: {value} cannot be casted to such type", 
                                           "results": []},
                                           400)
