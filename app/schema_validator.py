from marshmallow import Schema, fields, validate

from app.utils import REGEX_EMAIL

"""
Author: TienNguyen
CreatedDate: 15/01/2022 
"""


class CreateUserValidation(Schema):
    """
    Validator
    """
    password = fields.String(required=True, validate=validate.Length(min=1, max=50))
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    email = fields.String(required=True, validate=[validate.Length(min=3, max=50), validate.Regexp(REGEX_EMAIL)])
    username = fields.String(required=True, validate=validate.Length(min=1, max=50))
    status = fields.String(required=False, validate=validate.Length(min=1, max=50))


class LoginValidation(Schema):
    """
    Validator
    """
    password = fields.String(required=True, validate=validate.Length(min=1, max=50))
    username = fields.String(required=True, validate=validate.Length(min=1, max=50))
