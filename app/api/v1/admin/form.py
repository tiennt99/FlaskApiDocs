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
from app.schema_validator import GroupSchema, FormSchema, UpdateFormValidation, \
    CreateFormValidation, GetFormValidation
from app.models import User, Group, Form

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('forms', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_forms():
    """ This is api get all form by filter

    Returns: list form
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetFormValidation().load(params) if params else dict()
    except ValidationError as err:
        return send_error(message_id=FAIL, data=err.messages)

    # 2. Process input
    page_number = params.get('page', 1)
    page_size = params.get('page_size', 15)
    search_name = params.get('search_name', '')
    search_name = urllib.parse.unquote(search_name, encoding='utf-8', errors='replace').strip()
    search_name = escape_wildcard(search_name)
    sort_by = params.get('sort_by', None)
    order_by = params.get('order_by', 'desc')

    # 3. Query
    query = Form.query
    if len(search_name):
        query = query.filter(
            or_(Form.name.like("%{}%".format(search_name)),
                Form.description.like("%{}%".format(search_name))))
    # 4. Sort by collum
    if sort_by:
        column_sorted = getattr(User, sort_by)
        if order_by == 'asc':
            query = query.order_by(asc(column_sorted))
        else:
            query = query.order_by(desc(column_sorted))
    # Default: sort by created date
    else:
        query = query.order_by(Form.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    forms = FormSchema(many=True).dump(paginator.items)
    response_data = dict(
        forms=forms,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('', methods=['POST'])
@authorization_require()
def create_form():
    """ This is api create form

    Body: {
            "name": "Giảng viên",
            "description": "Nhập điểm"
        }
    Returns: SUCCESS/FAIL
    """
    try:
        json_body = request.get_json()
        current_user_id = get_jwt_identity()
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = CreateFormValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    form_id = str(uuid.uuid4())
    form = Form()
    for key in json_body.keys():
        form.__setattr__(key, json_body[key])
    form.id = form_id
    form.creator_id = current_user_id
    db.session.add(form)
    db.session.commit()
    return send_result(message_id=SUCCESS, data=FormSchema().dump(form))


@api.route('/<form_id>', methods=['PUT'])
@authorization_require()
def update_form(form_id: str):
    """ This is api update form

    :type form_id: string
    Body:   {
                "name": "Giảng viên",
                "description": "Nhập điểm",
                "role_ids": [
                    "3c0e7ac2-648a-11ec-90d6-0242ac120003",
                    "a55332a2-9998-4b92-9dc1-be000f4e1e45"
                    ]
            }
    Returns: user

    """
    try:
        json_body = request.get_json()
        current_user_id = get_jwt_identity()
        json_body["id"] = form_id
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = UpdateFormValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)

    # create form
    form = Form.get_by_id(form_id)
    for key in json_body.keys():
        form.__setattr__(key, json_body[key])
    form.creator_id = current_user_id
    db.session.add(form)
    db.session.commit()
    return send_result(data=FormSchema().dump(form), message_id=SUCCESS)


@api.route('/<form_id>', methods=['DELETE'])
@authorization_require()
def delete_form(form_id: str):
    """ This is api delete form

    :type form_id: string
    Returns: SUCCESS/False
    """
    form = Form.get_by_id(form_id)
    if not form:
        return send_error(message_id=FAIL)
    db.session.delete(form)
    db.session.commit()
    return send_result(message_id=SUCCESS)


@api.route('/<form_id>', methods=['GET'])
@authorization_require()
def get_by_id(form_id: str):
    form: Form = Form.get_by_id(form_id)
    if form is None:
        return send_error(message_id=FAIL)
    data_result = FormSchema().dump(form)
    return send_result(data=data_result)
