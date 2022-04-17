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
from app.schema_validator import SubjectSchema, GetSubjectValidation, CreateSubjectValidation, UpdateSubjectValidation
from app.models import User, Subject

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('admin/subjects', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_subjects():
    """ This is api get all subject by filter

    Returns: list subject
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetSubjectValidation().load(params) if params else dict()
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
    query = Subject.query
    if len(search_name):
        query = query.filter(
            or_(Subject.name.like("%{}%".format(search_name)),
                Subject.code.like("%{}%".format(search_name))))
    query = query.filter(and_(Subject.created_date > from_date, Subject.created_date < to_date))
    # 4. Sort by collum
    if sort_by:
        column_sorted = getattr(Subject, sort_by)
        if order_by == 'asc':
            query = query.order_by(asc(column_sorted))
        else:
            query = query.order_by(desc(column_sorted))
    # Default: sort by created date
    else:
        query = query.order_by(Subject.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    subjects = SubjectSchema(many=True).dump(paginator.items)
    response_data = dict(
        subjects=subjects,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('', methods=['POST'])
@authorization_require()
def create_subject():
    """ This is api create subject

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
    validator_input = CreateSubjectValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    subject_id = str(uuid.uuid4())
    subject = Subject()
    for key in json_body.keys():
        subject.__setattr__(key, json_body[key])
    subject.id = subject_id
    subject.creator_id = current_user_id
    db.session.add(subject)
    db.session.commit()
    return send_result(message_id=SUCCESS, data=SubjectSchema().dump(subject))


@api.route('/<subject_id>', methods=['PUT'])
@authorization_require()
def update_subject(subject_id: str):
    """ This is api update subject

    :type subject_id: string
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
        json_body["id"] = subject_id
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = UpdateSubjectValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)

    # create subject
    subject = Subject.get_by_id(subject_id)
    for key in json_body.keys():
        subject.__setattr__(key, json_body[key])
    subject.creator_id = current_user_id
    db.session.add(subject)
    db.session.commit()
    return send_result(data=SubjectSchema().dump(subject), message_id=SUCCESS)


@api.route('/<subject_id>', methods=['DELETE'])
@authorization_require()
def delete_subject(subject_id: str):
    """ This is api delete subject

    :type subject_id: string
    Returns: SUCCESS/False
    """
    subject = Subject.get_by_id(subject_id)
    if not subject:
        return send_error(message_id=FAIL)
    db.session.delete(subject)
    db.session.commit()
    return send_result(message_id=SUCCESS)


@api.route('/<subject_id>', methods=['GET'])
@authorization_require()
def get_by_id(subject_id: str):
    subject: Subject = Subject.get_by_id(subject_id)
    if subject is None:
        return send_error(message_id=FAIL)
    data_result = SubjectSchema().dump(subject)
    return send_result(data=data_result)
