import urllib
import uuid

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_, asc, desc, and_
from sqlalchemy_pagination import paginate
from werkzeug.security import generate_password_hash

from app.api.helper import send_error, send_result
from app.enums import FAIL, SUCCESS
from app.extensions import db
from app.gateway import authorization_require
from app.schema_validator import CreateUserValidation, UpdateUserValidation, UserSchema, GetUserValidation, RoleSchema
from app.models import User, Role

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('admin/users', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_users():
    """ This is api get all user by filter

    Returns: list users
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetUserValidation().load(params) if params else dict()
        current_user_id = get_jwt_identity()
        user = User.get_by_id(current_user_id)
        group_id = user.group.id
    except ValidationError as err:
        return send_error(message_id=FAIL, data=err.messages)

    # 2. Process input
    page_number = params.get('page', 1)
    page_size = params.get('page_size', 15)
    from_date = params.get('from_date', 0)
    to_date = params.get('to_date', get_timestamp_now())
    search_name = params.get('search_name', '')
    search_name = urllib.parse.unquote(search_name, encoding='utf-8', errors='replace').strip()
    search_name = escape_wildcard(search_name)
    sort_by = params.get('sort_by', None)
    order_by = params.get('order_by', 'desc')
    group_id = params.get('group_id', None)

    # 3. Query
    query = User.query
    if len(search_name):
        query = query.filter(
            or_(User.username.like("%{}%".format(search_name)),
                User.email.like("%{}%".format(search_name)),
                User.first_name.like("%{}%".format(search_name)),
                User.last_name.like("%{}%".format(search_name))))
    query = query.filter(and_(User.created_date > from_date, User.created_date < to_date))
    if group_id:
        query = query.filter(User.group_id == group_id)
    # 4. Sort by collum
    if sort_by:
        column_sorted = getattr(User, sort_by)
        if order_by == 'asc':
            query = query.order_by(asc(column_sorted))
        else:
            query = query.order_by(desc(column_sorted))
    # Default: sort by created date
    else:
        query = query.order_by(User.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    users = UserSchema(many=True).dump(paginator.items)
    response_data = dict(
        users=users,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('', methods=['POST'])
@authorization_require()
def create_user():
    """ This is api create user

    Body: {
          "first_name": "Anthia",
          "email":"test@gmail.com",
          "last_name": "Paumier",
          "username": "apaumier0",
          "password": "pqwjEghVUazZ",
          "group_id": ""
        }
    Returns: SUCCESS/FAIL
    """
    try:
        json_body = request.get_json()
        current_user_id = get_jwt_identity()

    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = CreateUserValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    user_id = str(uuid.uuid4())
    user = User()
    for key in json_body.keys():
        user.__setattr__(key, json_body[key])
    user.password_hash = generate_password_hash(user.password)
    user.id = user_id
    user.creator_id = current_user_id
    db.session.add(user)
    db.session.commit()
    return send_result(message_id=SUCCESS, data=UserSchema().dump(user))


@api.route('/<user_id>', methods=['PUT'])
@authorization_require()
def update_user(user_id: str):
    """ This is api update user

    :type user_id: string
    Body: {
          "first_name": "Anthia",
          "email":"test@gmail.com",
          "last_name": "Paumier",
          "username": "apaumier0",
          "password": "pqwjEghVUazZ",
          "group_id": ""
        }
    Returns: user

    """
    try:
        json_body = request.get_json()
        current_user_id = get_jwt_identity()
        json_body["id"] = user_id

    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = UpdateUserValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    user = User.get_by_id(user_id)
    for key in json_body.keys():
        user.__setattr__(key, json_body[key])
    user.creator_id = current_user_id
    db.session.add(user)
    db.session.commit()
    return send_result(data=UserSchema().dump(user), message_id=SUCCESS)


@api.route('/<user_id>', methods=['DELETE'])
@authorization_require()
def delete_user(user_id: str):
    """ This is api delete user

    :type user_id: string
    Returns: SUCCESS/False
    """
    user = User.get_by_id(user_id)
    if not user:
        return send_error(message_id=FAIL)
    db.session.delete(user)
    db.session.commit()
    return send_result(message_id=SUCCESS)


@api.route('/roles', methods=['GET'])
@authorization_require()
def get_role_permission():
    try:
        current_user_id = get_jwt_identity()
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    user = User.get_by_id(current_user_id)
    user_roles = user.group.roles
    roles = RoleSchema(many=True).dump(user_roles)
    response_data = dict(
        roles=roles
    )
    return send_result(data=response_data)


@api.route('/<user_id>', methods=['GET'])
@authorization_require()
def get_by_id(user_id: str):
    user: User = User.get_by_id(user_id)
    if user is None:
        return send_error(message_id=FAIL)
    data_result = UserSchema().dump(user)
    return send_result(data=data_result)


@api.route('/imports', methods=['POST'])
@authorization_require()
def import_users():
    try:
        current_user_id = get_jwt_identity()
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    user = User.get_by_id(current_user_id)
    user_roles = user.group.roles
    roles = RoleSchema(many=True).dump(user_roles)
    response_data = dict(
        roles=roles
    )
    return send_result(data=response_data)
