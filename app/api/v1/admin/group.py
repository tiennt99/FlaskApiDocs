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
from app.schema_validator import GetGroupValidation, CreateGroupValidation, GroupSchema, UpdateGroupValidation
from app.models import User, Group

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('group', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_groups():
    """ This is api get all group by filter

    Returns: list group
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetGroupValidation().load(params) if params else dict()
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
    query = Group.query
    if len(search_name):
        query = query.filter(
            or_(Group.name.like("%{}%".format(search_name)),
                Group.description.like("%{}%".format(search_name))))
    query = query.filter(and_(Group.created_date > from_date, Group.created_date < to_date))
    # 4. Sort by collum
    if sort_by:
        column_sorted = getattr(User, sort_by)
        if order_by == 'asc':
            query = query.order_by(asc(column_sorted))
        else:
            query = query.order_by(desc(column_sorted))
    # Default: sort by created date
    else:
        query = query.order_by(Group.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    groups = GroupSchema(many=True).dump(paginator.items)
    response_data = dict(
        groups=groups,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('', methods=['POST'])
@authorization_require()
def create_group():
    """ This is api create group

    Body: {
            "name": "Nhóm giáo viên",
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
    validator_input = CreateGroupValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    group = Group()
    for key in json_body.keys():
        group.__setattr__(key, json_body[key])

    db.session.add(group)
    db.session.commit()
    return send_result(message_id=SUCCESS)


@api.route('/<group_id>', methods=['PUT'])
@authorization_require()
def update_group(group_id: str):
    """ This is api update group

    :type group_id: string
    Body:   {
            "name": "Nhóm sinh viên",
            "description": "Thêm sửa xóa người dùng"
            }
    Returns: user

    """
    try:
        json_body = request.get_json()
        current_user_id = get_jwt_identity()
        json_body["creator_id"] = current_user_id
        json_body["id"] = group_id
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = UpdateGroupValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create group
    group = Group.get_group_by_id(group_id)
    for key in json_body.keys():
        group.__setattr__(key, json_body[key])

    db.session.add(group)
    db.session.commit()
    return send_result(data=GroupSchema().dump(group), message_id=SUCCESS)


@api.route('/<group_id>', methods=['DELETE'])
@authorization_require()
def delete_group(group_id: str):
    """ This is api delete group

    :type group_id: string
    Returns: SUCCESS/False
    """
    group = Group.get_group_by_id(group_id)
    if not group:
        return send_error(message_id=FAIL)
    db.session.delete(group)
    db.session.commit()
    return send_result(message_id=SUCCESS)
