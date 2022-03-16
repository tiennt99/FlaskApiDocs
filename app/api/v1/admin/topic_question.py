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
from app.schema_validator import GroupSchema, TopicSchema, UpdateTopicValidation, \
    CreateTopicValidation, GetTopicValidation
from app.models import User, Group, TopicQuestion

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('topics', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_topics():
    """ This is api get all topic by filter

    Returns: list topic
    """
    # 1. validate request parameters
    try:
        params = request.args
        params = GetTopicValidation().load(params) if params else dict()
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
    query = TopicQuestion.query
    if len(search_name):
        query = query.filter(
            or_(TopicQuestion.name.like("%{}%".format(search_name)),
                TopicQuestion.description.like("%{}%".format(search_name))))
    query = query.filter(and_(TopicQuestion.created_date > from_date, TopicQuestion.created_date < to_date))
    # 4. Sort by collum
    if sort_by:
        column_sorted = getattr(User, sort_by)
        if order_by == 'asc':
            query = query.order_by(asc(column_sorted))
        else:
            query = query.order_by(desc(column_sorted))
    # Default: sort by created date
    else:
        query = query.order_by(TopicQuestion.created_date.desc())

    # 5. Paginator
    paginator = paginate(query, page_number, page_size)
    # 6. Dump data
    topics = TopicSchema(many=True).dump(paginator.items)
    response_data = dict(
        topics=topics,
        total_pages=paginator.pages,
        total=paginator.total
    )
    return send_result(data=response_data)


@api.route('', methods=['POST'])
@authorization_require()
def create_topic():
    """ This is api create topic

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
    validator_input = CreateTopicValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    # create user
    topic_id = str(uuid.uuid4())
    topic = TopicQuestion()
    for key in json_body.keys():
        topic.__setattr__(key, json_body[key])
    topic.id = topic_id
    topic.creator_id = current_user_id
    db.session.add(topic)
    db.session.commit()
    return send_result(message_id=SUCCESS, data=TopicSchema().dump(topic))


@api.route('/<topic_id>', methods=['PUT'])
@authorization_require()
def update_topic(topic_id: str):
    """ This is api update topic

    :type topic_id: string
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
        json_body["id"] = topic_id
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = UpdateTopicValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)

    # create topic
    topic = TopicQuestion.get_topic_by_id(topic_id)
    for key in json_body.keys():
        topic.__setattr__(key, json_body[key])
    topic.creator_id = current_user_id
    db.session.add(topic)
    db.session.commit()
    return send_result(data=TopicSchema().dump(topic), message_id=SUCCESS)


@api.route('/<topic_id>', methods=['DELETE'])
@authorization_require()
def delete_topic(topic_id: str):
    """ This is api delete topic

    :type topic_id: string
    Returns: SUCCESS/False
    """
    topic = TopicQuestion.get_topic_by_id(topic_id)
    if not topic:
        return send_error(message_id=FAIL)
    db.session.delete(topic)
    db.session.commit()
    return send_result(message_id=SUCCESS)
