from flask import Blueprint

from backend.utils.jsonResult import req_success

test_api = Blueprint("test", __name__)


@test_api.route("/test", methods=["GET"])
def get_filelist():
    # wifi datas
    return req_success("SUCCESS", "Ok")
