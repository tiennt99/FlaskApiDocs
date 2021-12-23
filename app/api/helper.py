import os

from flask import jsonify

from app.models import Message
from app.settings import ProdConfig, DevConfig

# call config service


CONFIG = DevConfig if os.environ.get('FLASK_DEBUG') == '1' else ProdConfig


def send_result(data: any = None, message_id: str = '', message: str = "OK", code: int = 200,
                status: str = 'success', show: bool = False, duration: int = 0):
    """
    Args:
        data: simple result object like dict, string or list
        message: message send to client, default = OK
        code: code default = 200
        version: version of api
    :param data:
    :param message_id:
    :param message:
    :param code:
    :param status:
    :param show:
    :param duration:
    :return:
    json rendered sting result
    """
    message_dict = {
        "id": message_id,
        "text": message,
        "status": status,
        "show": show,
        "duration": duration,
    }
    message_obj: Message = Message.query.get(message_id)
    if message_obj:
        message_dict['text'] = message_obj.message
        message_dict['status'] = message_obj.status
        message_dict['show'] = message_obj.show
        message_dict['duration'] = message_obj.duration

    res = {
        "code": code,
        "data": data,
        "message": message_dict,
        "version": get_version(CONFIG.VERSION)
    }

    return jsonify(res), 200


def send_error(data: any = None, message_id: str = '', message: str = "Error", code: int = 200,
               status: str = 'error', show: bool = False, duration: int = 0):
    """

    :param data:
    :param message_id:
    :param message:
    :param code:
    :param status:
    :param show:
    :param duration:
    :return:
    """
    message_dict = {
        "id": message_id,
        "text": message,
        "status": status,
        "show": show,
        "duration": duration,
    }
    message_obj = Message.query.get(message_id)
    if message_obj:
        message_dict['text'] = message_obj.message
        message_dict['status'] = message_obj.status
        message_dict['show'] = message_obj.show
        message_dict['duration'] = message_obj.duration

    res = {
        "code": code,
        "data": data,
        "message": message_dict,
        "version": get_version(CONFIG.VERSION)
    }

    return jsonify(res), code


def get_version(version: str) -> str:
    """
    if version = 1, return api v1
    version = 2, return api v2
    Returns:

    """
    version_text = f"Flask v{version}"
    return version_text
