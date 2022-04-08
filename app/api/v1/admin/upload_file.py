import os

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from app.api.helper import send_result, send_error
from app.enums import FILE_PATH, URL_SERVER
from app.utils import get_timestamp_now
from app.schema_validator import UploadValidation

api = Blueprint('upload', __name__)


@api.route('', methods=['POST'])
@jwt_required
def upload_file():
    """ This api for.

        Request Body:

        Returns:

        Examples::

    """

    prefix = request.args.get('prefix', "", type=str).strip()

    # validate request params
    validator_upload = UploadValidation()
    is_invalid = validator_upload.validate({"prefix": prefix})
    if is_invalid:
        return send_error(data=is_invalid, message='Please check your request params')

    try:
        file = request.files['file']
    except Exception as ex:
        return send_error(message=str(ex))

    file_name = str(get_timestamp_now()) + secure_filename(file.filename)

    file_path = "{}/{}".format(prefix, file_name)
    path = os.path.join(FILE_PATH + file_path)
    file_url = os.path.join(URL_SERVER + file_path)
    try:
        file.save(path)
    except Exception as ex:
        return send_error(message=str(ex))
    dt = {
        "file_url": file_url
    }

    return send_result(data=dt, message="Ok")
