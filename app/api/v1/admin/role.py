import urllib
import uuid

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
from app.models import User, Role, Permission, RolePermission

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('admin/roles', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_roles():
    """ This is api get all role by filter

    Returns: list roles
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
        column_sorted = getattr(Role, sort_by)
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
    roles = RoleSchema(many=True).dump(paginator.items)
    response_data = dict(
        roles=roles,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('', methods=['POST'])
@authorization_require()
def create_role():
    """ This is api create role

    Body: {
                "name": "Xem danh sách quyền `1",
                "description": "Xem danh sách quyền",
                "permission_ids": [
                    "22ec23de-65f1-4f0f-8c7e-6b9122939444",
                    "31c284a8-552b-4f4f-a8c2-22ff998de895"
                ]
            }
    Returns: SUCCESS/FAIL
    """
    try:
        json_body = request.get_json()
        current_user_id = get_jwt_identity()
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = CreateRoleValidation()
    is_not_validate = validator_input.validate(json_body)
    permission_ids = json_body["permission_ids"]
    # check role exist
    number_permission = Permission.query.filter(Permission.id.in_(permission_ids)).count()
    if number_permission != len(permission_ids):
        return send_error(message="permission_ids không chính xác ")
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    role_id = str(uuid.uuid4())
    role = Role()
    for key in json_body.keys():
        role.__setattr__(key, json_body[key])
    role.id = role_id
    role.creator_id = current_user_id
    db.session.add(role)
    # add roles
    for permission_id in permission_ids:
        instance = RolePermission(id=str(uuid.uuid4()),
                                  role_id=role_id,
                                  permission_id=permission_id, creator_id=current_user_id)
        db.session.add(instance)
    db.session.commit()
    return send_result(message_id=SUCCESS)


@api.route('/<role_id>', methods=['PUT'])
@authorization_require()
def update_role(role_id: str):
    """ This is api update role

    :type role_id: string
    Body:   {
                "name": "Xem danh sách quyền `1",
                "description": "Xem danh sách quyền",
                "permissions": [
                    "22ec23de-65f1-4f0f-8c7e-6b9122939444",
                    "31c284a8-552b-4f4f-a8c2-22ff998de895"
                ]
            }
    Returns: user

    """
    try:
        json_body = request.get_json()
        current_user_id = get_jwt_identity()
        json_body["id"] = role_id
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = UpdateRoleValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    permission_ids = json_body["permission_ids"]
    # check role exist
    number_permission = Permission.query.filter(Permission.id.in_(permission_ids)).count()
    if number_permission != len(permission_ids):
        return send_error(message="permission_ids không chính xác ")
    # create role
    role = Role.get_by_id(role_id)
    for key in json_body.keys():
        role.__setattr__(key, json_body[key])
    role.creator_id = current_user_id
    db.session.add(role)

    # update role
    # Find out old members and new members
    current_role_permissions = RolePermission.query.filter(RolePermission.role_id == role_id).all()
    current_permission_ids = [group_role.role_id for group_role in current_role_permissions]
    new_permission_ids = list(set(permission_ids) - set(current_permission_ids))
    delete_role_ids = list(set(current_permission_ids) - set(permission_ids))
    # delete user in research group
    RolePermission.query.filter(RolePermission.role_id == role_id,
                                RolePermission.permission_id.in_(delete_role_ids)).delete()
    # insert user news in research_group
    for permission_id in new_permission_ids:
        instance = RolePermission(id=str(uuid.uuid4()),
                                  role_id=role_id,
                                  permission_id=permission_id, creator_id=current_user_id)
        db.session.add(instance)
    db.session.commit()
    return send_result(data=RoleSchema().dump(role), message_id=SUCCESS)


@api.route('/<role_id>', methods=['DELETE'])
@authorization_require()
def delete_role(role_id: str):
    """ This is api delete role

    :type role_id: string
    Returns: SUCCESS/False
    """
    role = Role.get_by_id(role_id)
    if not role:
        return send_error(message_id=FAIL)
    db.session.delete(role)
    db.session.commit()
    return send_result(message_id=SUCCESS)


@api.route('/<role_id>', methods=['GET'])
@authorization_require()
def get_by_id(role_id: str):
    role: Role = Role.get_by_id(role_id)
    if role is None:
        return send_error(message_id=FAIL)
    data_result = RoleSchema().dump(role)
    return send_result(data=data_result)
