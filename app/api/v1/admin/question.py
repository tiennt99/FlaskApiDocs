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
from app.schema_validator import GroupSchema, QuestionSchema, UpdateTopicValidation, \
    CreateQuestionValidation, GetQuestionValidation, CreateCommentValidation, GetQuestionDetailValidation, \
    CommentSchema, HistorySchema
from app.models import User, Group, Question, Comment, History

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('admin/questions', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_questions():
    """ This is api get all topic by filter

    Returns: list question
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetQuestionValidation().load(params) if params else dict()
        current_user_id = get_jwt_identity()
        user = User.get_by_id(current_user_id)
        group_name = user.group.name
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
    query = Question.query
    if len(search_name):
        query = query.filter(
            or_(Question.content.like("%{}%".format(search_name)),
                Question.description.like("%{}%".format(search_name))))
    query = query.filter(and_(Question.created_date > from_date, Question.created_date < to_date))
    if group_name != "Quản trị viên":
        query = query.filter(Question.assignee_user_id == current_user_id)
    # 4. Sort by collum
    if sort_by:
        column_sorted = getattr(Question, sort_by)
        if order_by == 'asc':
            query = query.order_by(asc(column_sorted))
        else:
            query = query.order_by(desc(column_sorted))
    # Default: sort by created date
    else:
        query = query.order_by(Question.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    questions = QuestionSchema(many=True).dump(paginator.items)
    response_data = dict(
        questions=questions,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('', methods=['POST'])
@authorization_require()
def create_question():
    """ This is api create question

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
    validator_input = CreateQuestionValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    question_id = str(uuid.uuid4())
    question = Question()
    for key in json_body.keys():
        question.__setattr__(key, json_body[key])
    question.id = question_id
    question.creator_id = current_user_id
    db.session.add(question)
    db.session.commit()
    return send_result(message_id=SUCCESS, data=QuestionSchema().dump(question))


@api.route('/<question_id>', methods=['PUT'])
@authorization_require()
def update_question(question_id: str):
    """ This is api update question

    :type question_id: string
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
        json_body["id"] = question_id
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = UpdateTopicValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)

    # create question
    question = Question.get_by_id(question_id)
    for key in json_body.keys():
        question.__setattr__(key, json_body[key])
    question.creator_id = current_user_id
    db.session.add(question)
    db.session.commit()
    return send_result(data=QuestionSchema().dump(question), message_id=SUCCESS)


@api.route('/<question_id>', methods=['DELETE'])
@authorization_require()
def delete_question(question_id: str):
    """ This is api delete question

    :type question_id: string
    Returns: SUCCESS/False
    """
    question = Question.get_by_id(question_id)
    if not question:
        return send_error(message_id=FAIL)
    db.session.delete(question)
    db.session.commit()
    return send_result(message_id=SUCCESS)


@api.route('/<question_id>', methods=['GET'])
@authorization_require()
def get_by_id(question_id: str):
    question: Question = Question.get_by_id(question_id)
    if question is None:
        return send_error(message_id=FAIL)
    data_result = QuestionSchema().dump(question)
    return send_result(data=data_result)


@api.route('/<question_id>/comments', methods=['GET'])
@authorization_require()
def get_detail_comment_question(question_id: str):
    """ This is api create comment

    Body: {
            "name": "Giảng viên",
            "description": "Nhập điểm"
        }
    Returns: SUCCESS/FAIL
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetQuestionDetailValidation().load(params) if params else dict()
    except ValidationError as err:
        return send_error(message_id=FAIL, data=err.messages)

    # 2. Process input
    page_number = params.get('page', 1)
    page_size = params.get('page_size', 15)

    # 3. Query
    query = Comment.query.filter(Comment.question_id == question_id)
    # Default: sort by created date
    query = query.order_by(Comment.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    comments = CommentSchema(many=True).dump(paginator.items)
    response_data = dict(
        comments=comments,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('/<question_id>/histories', methods=['GET'])
@authorization_require()
def get_detail_history_question(question_id: str):
    """ This is api create comment

    Body: {
            "name": "Giảng viên",
            "description": "Nhập điểm"
        }
    Returns: SUCCESS/FAIL
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetQuestionDetailValidation().load(params) if params else dict()
    except ValidationError as err:
        return send_error(message_id=FAIL, data=err.messages)

    # 2. Process input
    page_number = params.get('page', 1)
    page_size = params.get('page_size', 15)

    # 3. Query
    query = History.query.filter(History.question_id == question_id)
    # Default: sort by created date
    query = query.order_by(History.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    histories = HistorySchema(many=True).dump(paginator.items)
    response_data = dict(
        histories=histories,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('/<question_id>/comments', methods=['POST'])
@authorization_require()
def create_comment(question_id: str):
    """ This is api create comment

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
    json_body["question_id"] = question_id
    json_body["sender_id"] = current_user_id
    validator_input = CreateCommentValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    comment_id = str(uuid.uuid4())
    comment = Comment()
    for key in json_body.keys():
        comment.__setattr__(key, json_body[key])
    comment.id = comment_id
    db.session.add(comment)
    db.session.commit()
    return send_result(message_id=SUCCESS, data=CommentSchema().dump(comment))
