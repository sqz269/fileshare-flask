from fileshare import app

from flask import Blueprint, request

from fileshare.shared.libs import utils

import json

api_admin = Blueprint("admin_api", __name__, url_prefix="/api/admin")

@api_admin.route("/configuration/all", methods=["GET"])
def get_all_cfg():
    cfg_dump = json.dumps(app.config, sort_keys=True, default=str)
    return utils.make_json_resp_with_status({"status": 0, "details": "success", "results": cfg_dump}, 200)


@api_admin.route("/configuration/<string:key>", methods=["GET"])
def get_specific_cfg(key):
    try:
        return utils.make_json_resp_with_status({"status": 0, "details": "completed", "results": [app.config[key]]}, 200)
    except KeyError:
        return utils.make_json_resp_with_status({"status": 50, "details": f"no configurations is associated with key: {key}. note: most configuration keys are all caps letters", "results": []}, 400)


@api_admin.route("/configuration/<string:key>", methods=["POST"])
def update_configuration(key):
    try:
        value = get_url_param(request.args, "value")
        target_type = get_url_param(request.args, "type")

        old_value = app.config[key]
        value = utils.cvt_value_to_type(value, False, target_type)
        app.config[key] = value
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
