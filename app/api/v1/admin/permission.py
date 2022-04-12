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
from app.schema_validator import CreateGroupValidation, GroupSchema, UpdateGroupValidation, GetGroupValidation, \
    PermissionSchema
from app.models import User, Group, GroupRole, Role, Permission

from app.utils import escape_wildcard, get_timestamp_now

api = Blueprint('admin/permissions', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_permissions():
    """ This is api get all permission by filter

    Returns: list permission
    """
    permissions = Permission.query.all()
    permissions = PermissionSchema(many=True).dump(permissions)
    list_id = [item.get("id") for item in permissions]
    return send_result(data=list_id)

