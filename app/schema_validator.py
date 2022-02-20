import uuid
from builtins import float

from marshmallow import Schema, fields, validate, pre_load, validates, ValidationError, validates_schema

from app.enums import LIST_GROUP
from app.models import User, Role, Group
from app.utils import REGEX_EMAIL

"""
Author: TienNguyen
CreatedDate: 15/01/2022 
"""


# Manage User
class CreateUserValidation(Schema):
    """
    Validator
    """
    password = fields.String(required=True, validate=validate.Length(min=1, max=50))
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    email = fields.String(required=True, validate=[validate.Length(min=3, max=50), validate.Regexp(REGEX_EMAIL)])
    username = fields.String(required=True, validate=validate.Length(min=1, max=50))
    status = fields.String(required=False)
    creator_id = fields.String(required=False)
    group_id = fields.String(required=True, validate=validate.OneOf(LIST_GROUP))

    @validates("email")
    def validate_email(self, value):
        if User.check_user_exists(value):
            raise ValidationError("Email đã tồn tại")

    @validates("username")
    def validate_username(self, value):
        if User.check_user_exists(value):
            raise ValidationError("Username đã tồn tại")

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["email"] = data["email"].lower().strip()
        data["username"] = data["username"].lower().strip()
        return data


class UpdateUserValidation(Schema):
    """
    Validator
    """
    id = fields.String(required=False)
    password = fields.String(required=True, validate=validate.Length(min=1, max=50))
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    email = fields.String(required=True, validate=[validate.Length(min=3, max=50), validate.Regexp(REGEX_EMAIL)])
    username = fields.String(required=True, validate=validate.Length(min=1, max=50))
    status = fields.String(required=False)
    creator_id = fields.String(required=False)
    group_id = fields.String(required=True, validate=validate.OneOf(LIST_GROUP))

    # # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["email"] = data["email"].lower().strip()
        data["username"] = data["username"].lower().strip()
        return data

    @validates_schema
    def validate_name(self, data, **kwargs):
        if User.check_user_exists(data["username"], data["id"]):
            raise ValidationError('Username đã tồn tại')

    @validates_schema
    def validate_email(self, data, **kwargs):
        if User.check_user_exists(data["email"], data["id"]):
            raise ValidationError('Email đã tồn tại')


class UserSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    password = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String()
    username = fields.String()
    status = fields.String()
    creator_id = fields.String()
    group_id = fields.String(required=True, validate=validate.OneOf(LIST_GROUP))


class GetUserValidation(Schema):
    """
    """
    page = fields.Integer(required=False)
    page_size = fields.Integer(required=False)
    from_date = fields.Integer(required=False)
    to_date = fields.Integer(required=False)
    search_name = fields.String(required=False)

    sort_by = fields.String(required=False,
                            validate=validate.OneOf(
                                ["username", "email", "first_name", "last_name", "created_date", "modified_date"]))
    order_by = fields.String(required=False, validate=validate.OneOf(["asc", "desc"]))


# Manage Role
class CreateRoleValidation(Schema):
    """
    Validator
    """
    name = fields.String(required=True)
    description = fields.String(required=False)
    creator_id = fields.String(required=False)
    permission_ids = fields.List(fields.String(required=False))

    @validates("name")
    def validate_name(self, value):
        if Role.check_role_exists(value):
            raise ValidationError("Role đã tồn tại")

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].lower().strip()
        data["description"] = data["description"].lower().strip() if data["description"] else None
        return data


class UpdateRoleValidation(Schema):
    """
    Validator
    """
    id = fields.String(required=False)
    name = fields.String(required=True)
    description = fields.String(required=False)
    creator_id = fields.String(required=False)
    permission_ids = fields.List(fields.String(required=False))

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].strip()
        data["description"] = data["description"].lower().strip() if data["description"] else None
        return data

    @validates_schema
    def validate_name(self, data, **kwargs):
        if Role.check_role_exists(data["name"], data["id"]):
            raise ValidationError('Role đã tồn tại')


class PermissionSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    name = fields.String()
    resource = fields.String()


class RoleSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    name = fields.String()
    description = fields.String()
    creator_id = fields.String(required=False)
    permissions = fields.List(fields.Nested(PermissionSchema(only=["id", "name"])))


class GetRoleValidation(Schema):
    """
    """
    page = fields.Integer(required=False)
    page_size = fields.Integer(required=False)
    from_date = fields.Integer(required=False)
    to_date = fields.Integer(required=False)
    search_name = fields.String(required=False)

    sort_by = fields.String(required=False,
                            validate=validate.OneOf(
                                ["name", "created_date", "modified_date"]))
    order_by = fields.String(required=False, validate=validate.OneOf(["asc", "desc"]))


# Manage Group
class CreateGroupValidation(Schema):
    """
    Validator
    """
    name = fields.String(required=True)
    description = fields.String(required=False)
    role_ids = fields.List(fields.String(required=False))

    @validates("name")
    def validate_name(self, value):
        if Group.check_group_exists(value):
            raise ValidationError("Group đã tồn tại")

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].lower().strip()
        data["description"] = data["description"].lower().strip() if data["description"] else None
        return data


class UpdateGroupValidation(Schema):
    """
    Validator
    """
    id = fields.String(required=False)
    name = fields.String(required=True)
    description = fields.String(required=False)
    creator_id = fields.String(required=False)
    role_ids = fields.List(fields.String(required=False))

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].strip()
        data["description"] = data["description"].strip() if data["description"] else None
        return data

    @validates_schema
    def validate_name(self, data, **kwargs):
        if Group.check_group_exists(data["name"], data["id"]):
            raise ValidationError('Group đã tồn tại')


class GroupSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    name = fields.String()
    description = fields.String()
    creator_id = fields.String(required=False)
    creator = fields.Nested(UserSchema(only=['id', 'email']))
    roles = fields.List(fields.Nested(RoleSchema(only=['id', 'name'])))


class GetGroupValidation(Schema):
    """
    """
    page = fields.Integer(required=False)
    page_size = fields.Integer(required=False)
    from_date = fields.Integer(required=False)
    to_date = fields.Integer(required=False)
    search_name = fields.String(required=False)

    sort_by = fields.String(required=False,
                            validate=validate.OneOf(
                                ["name", "created_date", "modified_date"]))
    order_by = fields.String(required=False, validate=validate.OneOf(["asc", "desc"]))


# Login

class LoginValidation(Schema):
    """
    Validator
    """
    password = fields.String(required=True, validate=validate.Length(min=1, max=50))
    username = fields.String(required=True, validate=validate.Length(min=1, max=50))
