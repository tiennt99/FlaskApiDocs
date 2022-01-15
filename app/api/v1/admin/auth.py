from datetime import timedelta
from flask import Blueprint, request
from app.extensions import jwt, logger
from app.api.helper import send_error, send_result, get_permissions
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, get_jwt_identity,
    create_refresh_token, get_raw_jwt)
from app.models import User, Token
from app.schema_validator import LoginValidation
from sqlalchemy import or_, and_
from app.enums import SUCCESS, FAIL, LOGIN_WRONG_USERNAME, LOGIN_WRONG_PASSWORD
from app.utils import password_encode

ACCESS_EXPIRES = timedelta(days=30)
REFRESH_EXPIRES = timedelta(days=90)
api = Blueprint('auth', __name__)


@api.route('/login', methods=['POST'])
def login():
    """

    Returns:

    """
    try:
        json_data = request.get_json()
        # Check valid params
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    try:
        json_body = request.get_json()
    except Exception as ex:
        return send_error(message="Request Body incorrect json format: " + str(ex), code=442)
    # validate request body
    validator_input = LoginValidation()
    is_not_validate = validator_input.validate(json_body)
    if is_not_validate:
        return send_error(data=is_not_validate, message_id=FAIL)
    username = json_data.get('username', '').lower().strip()
    password = json_data.get('password', '').strip()
    # Check input
    user = User.query.filter(or_(User.username == username, User.email == username)).first()
    if user is None:
        return send_error(message_id=LOGIN_WRONG_USERNAME)
    if password_encode(password) != user.password:
        return send_error(message_id=LOGIN_WRONG_PASSWORD)
    # get info user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    list_permission = ["delete@/api/v1/admin/auth/logout",
                       "post@/api/v1/admin/auth/sign-in",
                       "post@/api/v1/admin/auth/token/refresh",
                       "post@/api/v1/admin/users",
                       "get@/api/v1/helper/site-map",
                       "get@/static/<path:filename>"]
    access_token = create_access_token(identity=str(user.id), expires_delta=ACCESS_EXPIRES,
                                       user_claims={"list_permission": list_permission})
    refresh_token = create_refresh_token(identity=str(user.id), expires_delta=REFRESH_EXPIRES,
                                         user_claims={"list_permission": list_permission})
    # access_token = create_access_token(identity=str(user_id), expires_delta=ACCESS_EXPIRES)
    # refresh_token = create_refresh_token(identity=str(user_id), expires_delta=REFRESH_EXPIRES)
    Token.add_token_to_database(access_token, user.id)
    Token.add_token_to_database(refresh_token, user.id)
    data = dict(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
    )
    return send_result(data=data, message_id=SUCCESS)


@api.route('token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """
    Refresh token if token is expired
    :return:
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id, expires_delta=ACCESS_EXPIRES)
    refresh_token = create_refresh_token(identity=current_user_id, expires_delta=REFRESH_EXPIRES)
    Token.add_token_to_database(access_token, current_user_id)
    Token.add_token_to_database(refresh_token, current_user_id)
    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': current_user_id
    }
    return send_result(data=data)


# Endpoint for revoking the current users access token
@api.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    """
    Add token to blacklist
    :return:
    """
    jti = get_raw_jwt()['jti']

    Token.revoke_token(jti)
    logger.info("Logout Successfully")
    return send_result(message='Logout Successfully')


# check token revoked_store
@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    return Token.is_token_revoked(decrypted_token)
# # Endpoint for revoking the current users refresh token
# @api.route('/logout2', methods=['DELETE'])
# @jwt_refresh_token_required
# def logout2():
#     jti = get_raw_jwt()['jti']
#     # revoked_store.set(jti, 'true', REFRESH_EXPIRES * 1.2)
#     return send_result(message='logout_successfully')
#
#
# # check token revoked_store
# @jwt.token_in_blacklist_loader
# def check_if_token_is_revoked(decrypted_token):
#     jti = decrypted_token['jti']
#     # entry = revoked_store.get(jti)
#     # if entry is None:
#     #     return True
#     return False
