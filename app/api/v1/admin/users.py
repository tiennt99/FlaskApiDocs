from flask import Blueprint, request

from app.api.helper import send_error, send_result
from app.extensions import db
from app.schema_validator import CreateUserValidation
from app.models import Users
import uuid

api = Blueprint('users', __name__)


@api.route('', methods=['POST'])
def create_user():
    """

    Returns:

    """
    try:
        json_body = request.get_json()
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)

    validator_input = CreateUserValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id='0')

    json_body['id'] = str(uuid.uuid1())
    user = Users()
    for key in json_body.keys():
        user.__setattr__(key, json_body[key])

    db.session.add(user)
    db.session.commit()
    data = {
        "user_id": user.id
    }

    return send_result(data=data)
