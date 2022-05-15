from flask import Blueprint

from app.api.helper import send_result
from app.gateway import authorization_require
from app.models import Permission
from app.schema_validator import PermissionSchema

api = Blueprint('admin/permissions', __name__)


@api.route('', methods=['GET'])
@authorization_require()
def get_permissions():
    """ This is api get all permission by filter

    Returns: list permission
    """
    permissions = Permission.query.all()
    permissions = PermissionSchema(many=True).dump(permissions)

    return send_result(data=permissions)

