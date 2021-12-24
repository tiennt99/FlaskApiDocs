from marshmallow import Schema, fields, validate


class CreateUserValidation(Schema):
    """
    Validator
    """
    password = fields.String(required=True, validate=validate.Length(min=1, max=50))
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    email = fields.String(required=True, validate=validate.Length(min=1, max=50))
    username = fields.String(required=True, validate=validate.Length(min=1, max=50))
    status = fields.String(required=False, validate=validate.Length(min=1, max=50))
    type = fields.String(required=False, validate=validate.Length(min=1, max=50))


class RoleSchema(Schema):
    """
    Marshmallow Schema
    Author: phongnv
    Target: Use for permission
    """
    id = fields.String()
    key = fields.String()
    name = fields.String()
    description = fields.String()
    is_show = fields.Boolean()
    type = fields.Integer()


class PermissionSchema(Schema):
    """
    Marshmallow Schema
    Author: LyChan
    Target: Use for permission
    """
    id = fields.String()
    name = fields.String()
    resource = fields.String()


class RolePermissionSchema(Schema):
    """
    Marshmallow Schema
    Author: LyChan
    Target: Use for permission
    """
    id = fields.String()
    role_id = fields.String()
    permission_id = fields.String()

# user_validator = {
#     "type": "object",
#     "properties": {
#         "password": {
#             "type": "string",
#             "minLength": 3,
#             "maxLength": 50
#         },
#         "first_name": {
#             "type": "string",
#             "minLength": 1,
#             "maxLength": 50
#         },
#         "last_name": {
#             "type": "string",
#             "minLength": 1,
#             "maxLength": 50
#         },
#         "email": {
#             "type": "string",
#             "minLength": 1,
#             "maxLength": 50
#         },
#         "status": {
#             "type": "string",
#             "minLength": 1,
#             "maxLength": 50
#         },
#         "type": {
#             "type": "string",
#             "minLength": 1,
#             "maxLength": 50
#         }
#     },
#     "required": ["first_name", "last_name", "email", "status", "password", "type"]
# }
# signin_validator = {
#     "type": "object",
#     "properties": {
#         "email": {
#             "type": "string",
#             "minLength": 3,
#             "maxLength": 50
#         },
#         "password": {
#             "type": "string",
#             "minLength": 3,
#             "maxLength": 50
#         }
#     },
#     "required": ["email","password"]
# }
# password_validator = {
#     "type": "object",
#     "properties": {
#         "current_password": {
#             "type": "string",
#             "minLength": 3,
#             "maxLength": 50
#         },
#         "new_password": {
#             "type": "string",
#             "minLength": 3,
#             "maxLength": 50
#         }
#     },
#     "required": ["new_password"]
# }
#
# property_validator = {
#     "type": "object",
#     "properties": {
#         "name": {
#             "type": "string",
#             "maxLength": 100
#         },
#         "address": {
#             "type": "string",
#             "maxLength": 100
#         },
#         "phone": {
#             "type": "string",
#             "maxLength": 50
#         },
#         "distance_from_center": {
#             "type": "number",
#             "minimum": 0
#         },
#         "description": {
#             "type": "string",
#             "maxLength": 1000
#         },
#         "is_near_beach": {
#             "type": "number",
#             "minimum": 0,
#             "maximum": 1
#         },
#         "rank": {
#             "type": "number",
#             "minimum": 0,
#             "maximum": 5
#         },
#         "meal": {
#             "type": "number",
#             "minimum": 0,
#             "maximum": 4
#         },
#         "city_id": {
#             "type": "string",
#             "maxLength": 50
#         },
#         "property_type_id": {
#             "type": "string",
#             "maxLength": 50
#         }
#     },
#     "required": ["name", "address", "phone", "distance_from_center", "description", "is_near_beach", "rank", "meal",
#                  "city_id", "property_type_id"]
# }
#
# room_validator = {
#     "type": "object",
#     "properties": {
#         "name": {
#             "type": "string",
#             "maxLength": 100
#         },
#         "acreage": {
#             "type": "number",
#             "minimum": 0
#         },
#         "price": {
#             "type": "number",
#             "minimum": 0
#         },
#         "facility": {
#             "type": "string",
#             "maxLength": 200
#         },
#         "description": {
#             "type": "string",
#             "maxLength": 1000
#         },
#         "bed_type": {
#             "type": "number",
#             "minimum": 0,
#             "maximum": 1
#         },
#         "property_id": {
#             "type": "string",
#             "maxLength": 50
#         }
#     },
#     "required": []
# }
#
# city_validator = {
#     "type": "object",
#     "properties": {
#         "name": {
#             "type": "string",
#             "maxLength": 100
#         },
#         "description": {
#             "type": "string",
#             "maxLength": 1000
#         },
#         "image": {
#             "type": "string",
#             "maxLength": 50
#         }
#     },
#     "required": ["name", "description", "image"]
# }
#
# property_type_validator = {
#     "type": "object",
#     "properties": {
#         "name": {
#             "type": "string",
#             "maxLength": 100
#         },
#         "description": {
#             "type": "string",
#             "maxLength": 1000
#         },
#         "image": {
#             "type": "string",
#             "maxLength": 50
#         }
#     },
#     "required": ["name", "description", "image"]
# }
#
# booking_validator = {
#     "type": "object",
#     "properties": {
#         "room_id": {
#             "type": "string",
#             "maxLength": 50
#         },
#         "date_check_in": {
#             "type": "number",
#             "minimum": 0
#         },
#         "date_check_out": {
#             "type": "number",
#             "minimum": 0
#         },
#         "service": {
#             "type": "string",
#             "maxLength": 500
#         },
#         "note": {
#             "type": "string",
#             "maxLength": 500
#         },
#         "total": {
#             "type": "number",
#             "minimum": 0
#         },
#         "is_cancel": {
#             "type": "number",
#             "minimum": 0,
#             "maximum": 1,
#         }
#     },
#     "required": []
# }
#
# feature_validator = {
#     "type": "object",
#     "properties": {
#         "acreage": {
#             "type": "number",
#             "minimum": 0
#         },
#         "bed_type": {
#             "type": "number",
#             "minimum": 0,
#             "maximum": 1
#         },
#         "is_near_beach": {
#             "type": "number",
#             "minimum": 0,
#             "maximum": 1
#         },
#         "rank": {
#             "type": "number",
#             "minimum": 0,
#             "maximum": 5
#         },
#         "meal": {
#             "type": "number",
#             "minimum": 0,
#             "maximum": 4
#         },
#         "distance_from_center": {
#             "type": "number",
#             "minimum": 0
#         },
#         "city_id": {
#             "type": "string"
#         },
#         "property_type_id": {
#             "type": "string"
#         }
#     },
#     "required": ["acreage", "bed_type", "distance_from_center", "is_near_beach", "rank", "meal", "city_id",
#                  "property_type_id"]
# }
# data_validator = {
#     "type": "object",
#     "properties": {
#         "title": {
#             "type": "string"
#         },
#         "description": {
#             "type": "string",
#         }
#     },
#     "required": ["title", "description"]
# }
