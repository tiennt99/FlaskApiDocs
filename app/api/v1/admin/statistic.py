import time
import urllib
import uuid
from collections import Counter
from datetime import datetime, timedelta
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import asc, desc, and_, func
from sqlalchemy_pagination import paginate
from app.api.helper import send_error, send_result
from app.enums import FAIL, SUCCESS
from app.extensions import db
from app.gateway import authorization_require
from app.schema_validator import FrequentQuestionSchema, UpdateFrequentQuestionValidation, \
    CreateFrequentQuestionValidation, GetFrequentQuestionValidation, GetStatisticQuestionValidation, QuestionSchema, \
    TopicSchema, StatisticTopicSchema
from app.models import User, FrequentQuestion, Question, TopicQuestion, session
from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('admin/statistics', __name__)


@api.route('/questions', methods=['GET'])
@authorization_require()
def get_questions():
    """ This is api get all dashboard by filter

    Returns: list dashboard
    """

    # 1. validate request parameters
    try:
        params = request.args
        params = GetStatisticQuestionValidation().load(params) if params else dict()
    except ValidationError as err:
        return send_error(message_id=FAIL, data=err.messages)

    # 2. Process input
    time_now = time.time()
    from_date = params.get('from_date', time_now - 7 * 86400)
    to_date = params.get('to_date', time_now)

    questions = Question.query.filter(Question.created_date >= from_date, Question.created_date <= to_date).all()
    json_questions = QuestionSchema(many=True, only=["created_date"]).dump(questions)
    # delta time
    delta = timedelta(days=1)
    from_datetime = datetime.fromtimestamp(from_date)
    to_datetime = datetime.fromtimestamp(to_date)
    list_created_dates = list()
    while from_datetime <= to_datetime:
        list_created_dates.append(from_datetime.strftime('%d-%m-%Y'))
        from_datetime += delta

    for json_question in json_questions:
        list_created_dates.append(datetime.fromtimestamp(json_question.get("created_date", None)).strftime('%d-%m-%Y'))
    statistic_questions = list()
    counter_questions = Counter(list_created_dates)
    for created_date, value in counter_questions.items():
        statistic_questions.append(dict(
            created_date=created_date,
            number_of_questions=value - 1
        ))
    response_data = dict(
        statistic_questions=statistic_questions
    )
    return send_result(data=response_data)


@api.route('/topics', methods=['GET'])
@authorization_require()
def get_topics():
    """
    number_of_articles_by_date = session.query(
        func.date_format(Article.crawl_datetime, "%Y-%m-%d").label("crawl_datetime"),
        func.count(Article.id).label("number_of_article")). \
        filter(func.date_format(Article.crawl_datetime, "%Y-%m-%d") > from_date,
               func.date_format(Article.crawl_datetime, "%Y-%m-%d") < to_date). \
        group_by(func.date_format(Article.crawl_datetime, search_mapping.get(search_by, '%Y-%m-%d'))).all()
    """
    topics = db.session.query(func.count(Question.id).label("number_of_questions"), TopicQuestion.name). \
        join(Question, Question.topic_id == TopicQuestion.id, isouter=True).group_by(TopicQuestion.name).all()
    statistic_topics = StatisticTopicSchema(many=True).dump(topics)

    response_data = dict(
        statistic_topics=statistic_topics
    )
    return send_result(data=response_data)
