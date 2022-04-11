import urllib
import uuid

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import asc, desc, and_
from sqlalchemy_pagination import paginate
from app.api.helper import send_error, send_result
from app.enums import FAIL, SUCCESS
from app.extensions import db
from app.gateway import authorization_require
from app.schema_validator import FrequentQuestionSchema, UpdateFrequentQuestionValidation, \
    CreateFrequentQuestionValidation, GetFrequentQuestionValidation
from app.models import User, FrequentQuestion

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('frequent_questions', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_frequent_questions():
    """ This is api get all frequent_question by filter

    Returns: list frequent_question
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetFrequentQuestionValidation().load(params) if params else dict()
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
    query = FrequentQuestion.query
    if len(search_name):
        query = query.filter(FrequentQuestion.question.like("%{}%".format(search_name)))
    query = query.filter(and_(FrequentQuestion.created_date > from_date, FrequentQuestion.created_date < to_date))
    # 4. Sort by column
    if sort_by:
        column_sorted = getattr(User, sort_by)
        if order_by == 'asc':
            query = query.order_by(asc(column_sorted))
        else:
            query = query.order_by(desc(column_sorted))
    # Default: sort by created date
    else:
        query = query.order_by(FrequentQuestion.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    frequent_questions = FrequentQuestionSchema(many=True).dump(paginator.items)
    response_data = dict(
        frequent_questions=frequent_questions,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('', methods=['POST'])
@authorization_require()
def create_frequent_question():
    """ This is api create frequent_question

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
    validator_input = CreateFrequentQuestionValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    frequent_question_id = str(uuid.uuid4())
    frequent_question = FrequentQuestion()
    for key in json_body.keys():
        frequent_question.__setattr__(key, json_body[key])
    frequent_question.id = frequent_question_id
    frequent_question.creator_id = current_user_id
    db.session.add(frequent_question)
    db.session.commit()
    return send_result(message_id=SUCCESS, data=FrequentQuestionSchema().dump(frequent_question))


@api.route('/<frequent_question_id>', methods=['PUT'])
@authorization_require()
def update_frequent_question(frequent_question_id: str):
    """ This is api update frequent_question

    :type frequent_question_id: string
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
        json_body["id"] = frequent_question_id
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = UpdateFrequentQuestionValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)

    # create frequent_question
    frequent_question = FrequentQuestion.get_by_id(frequent_question_id)
    for key in json_body.keys():
        frequent_question.__setattr__(key, json_body[key])
    frequent_question.creator_id = current_user_id
    db.session.add(frequent_question)
    db.session.commit()
    return send_result(data=FrequentQuestionSchema().dump(frequent_question), message_id=SUCCESS)


@api.route('/<frequent_question_id>', methods=['DELETE'])
@authorization_require()
def delete_frequent_question(frequent_question_id: str):
    """ This is api delete frequent_question

    :type frequent_question_id: string
    Returns: SUCCESS/False
    """
    frequent_question = FrequentQuestion.get_by_id(frequent_question_id)
    if not frequent_question:
        return send_error(message_id=FAIL)
    db.session.delete(frequent_question)
    db.session.commit()
    return send_result(message_id=SUCCESS)


@api.route('/<frequent_question_id>', methods=['GET'])
@authorization_require()
def get_by_id(frequent_question_id: str):
    frequent_question: FrequentQuestion = FrequentQuestion.get_by_id(frequent_question_id)
    if frequent_question is None:
        return send_error(message_id=FAIL)
    data_result = FrequentQuestionSchema().dump(frequent_question)
    return send_result(data=data_result)
