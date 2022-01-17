import urllib

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_, asc, desc, and_
from sqlalchemy_pagination import paginate
from app.api.helper import send_error, send_result
from app.enums import FAIL, SUCCESS
from app.extensions import db
from app.gateway import authorization_require
from app.schema_validator import UpdateRoleValidation, GetRoleValidation, CreateRoleValidation, RoleSchema
from app.models import User, Role

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('role', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_roles():
    """ This is api get all role by filter

    Returns: list users
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetRoleValidation().load(params) if params else dict()
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

    # 3. Query
    query = Role.query
    if len(search_name):
        query = query.filter(
            or_(Role.name.like("%{}%".format(search_name)),
                Role.description.like("%{}%".format(search_name))))
    query = query.filter(and_(Role.created_date > from_date, Role.created_date < to_date))
    # 4. Sort by collum
    if sort_by:
        column_sorted = getattr(User, sort_by)
        if order_by == 'asc':
            query = query.order_by(asc(column_sorted))
        else:
            query = query.order_by(desc(column_sorted))
    # Default: sort by created date
    else:
        query = query.order_by(Role.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    users = RoleSchema(many=True).dump(paginator.items)
    response_data = dict(
        roles=users,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('', methods=['POST'])
@authorization_require()
def create_role():
    """ This is api create role

    Body: {
            "name": "Quản trị người dùng",
            "description": "Thêm sửa xóa người dùng"
            }
    Returns: SUCCESS/FAIL
    """
    try:
        json_body = request.get_json()
        current_user_id = get_jwt_identity()
        json_body["creator_id"] = current_user_id
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = CreateRoleValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    role = Role()
    for key in json_body.keys():
        role.__setattr__(key, json_body[key])

    db.session.add(role)
    db.session.commit()
    return send_result(message_id=SUCCESS)


@api.route('/<role_id>', methods=['PUT'])
@authorization_require()
def update_role(role_id: str):
    """ This is api update role

    :type role_id: string
    Body:   {
            "name": "Quản trị người dùng",
            "description": "Thêm sửa xóa người dùng"
            }
    Returns: user

    """
    try:
        json_body = request.get_json()
        current_user_id = get_jwt_identity()
        json_body["creator_id"] = current_user_id
        json_body["id"] = role_id
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = UpdateRoleValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create role
    role = Role.get_role_by_id(role_id)
    for key in json_body.keys():
        role.__setattr__(key, json_body[key])

    db.session.add(role)
    db.session.commit()
    return send_result(data=RoleSchema().dump(role), message_id=SUCCESS)


@api.route('/<role_id>', methods=['DELETE'])
@authorization_require()
def delete_role(role_id: str):
    """ This is api delete role

    :type role_id: string
    Returns: SUCCESS/False
    """
    role = Role.get_role_by_id(role_id)
    if not role:
        return send_error(message_id=FAIL)
    db.session.delete(role)
    db.session.commit()
    return send_result(message_id=SUCCESS)
