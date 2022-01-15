from flask import Blueprint, request

from app.api.helper import send_error, send_result
from app.enums import FAIL, SUCCESS
from app.extensions import db
from app.gateway import authorization_require
from app.schema_validator import CreateUserValidation
from app.models import User
import uuid

api = Blueprint('users', __name__)


@api.route('', methods=['POST'])
@authorization_require()
def create_user():
    """
    Body: {
          "first_name": "Anthia",
          "email":"test@gmail.com",
          "last_name": "Paumier",
          "username": "apaumier0",
          "password": "pqwjEghVUazZ",
          "group_id": ""
        }
    Returns: user_id
    """
    try:
        json_body = request.get_json()
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = CreateUserValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # check condition

    # create user
    json_body['id'] = str(uuid.uuid1())
    user = User()
    for key in json_body.keys():
        user.__setattr__(key, json_body[key])

    db.session.add(user)
    db.session.commit()
    result = {
        "user_id": user.id
    }

    return send_result(data=result, message_id=SUCCESS)
