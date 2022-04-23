from marshmallow import Schema, fields, validate, pre_load, validates, ValidationError, validates_schema

from app.enums import LIST_GROUP
from app.models import User, Role, Group, TopicQuestion, Subject, FrequentQuestion, Form, Question
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


class ChangePasswordValidator(Schema):
    old_password = fields.String(required=True, validate=validate.Length(min=1, max=50))
    new_password = fields.String(required=True, validate=validate.Length(min=1, max=50))


class UserSchemaTMP(Schema):
    id = fields.String()
    email = fields.String()


class UserSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    password = fields.String()
    password_hash = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String()
    username = fields.String()
    status = fields.String()
    avatar_url = fields.String()
    creator_id = fields.String()
    creator = fields.Nested(UserSchemaTMP(only=['id', 'email']))
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
    module = fields.String()
    description = fields.String()
    creator_id = fields.String(required=False)
    creator = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))
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


class CreateTopicValidation(Schema):
    """
    Validator
    """
    name = fields.String(required=True)
    description = fields.String(required=False)

    @validates("name")
    def validate_name(self, value):
        if TopicQuestion.check_topic_exists(value):
            raise ValidationError("Topic đã tồn tại")

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].lower().strip()
        data["description"] = data["description"].lower().strip() if data["description"] else None
        return data


class CreateCommentValidation(Schema):
    """
    Validator
    """
    message = fields.String(required=True)
    attached_file_url = fields.String(required=False)
    sender_id = fields.String(required=True)
    question_id = fields.String(required=True)


class CreateQuestionValidation(Schema):
    """
    Validator
    """
    description = fields.String(required=False)
    title = fields.String(required=False)
    attached_file_url = fields.String(required=False)
    topic_id = fields.String(required=False)
    user_id = fields.String(required=True)
    assignee_user_id = fields.String(required=True)
    status = fields.String(required=False)

    @validates("title")
    def validate_name(self, value):
        if Question.check_question_exists(value):
            raise ValidationError("Question đã tồn tại")

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["title"] = data["title"].lower().strip() if data["title"] else None
        data["description"] = data["description"].lower().strip() if data["description"] else None
        return data


class CreateFormValidation(Schema):
    """
    Validator
    """
    name = fields.String(required=True)
    description = fields.String(required=False)
    link = fields.String(required=True)

    @validates("name")
    def validate_name(self, value):
        if Form.check_form_exists(value):
            raise ValidationError("Form đã tồn tại")

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].lower().strip()
        data["description"] = data["description"].lower().strip() if data["description"] else None
        return data


class CreateFrequentQuestionValidation(Schema):
    """
    Validator
    """
    question = fields.String(required=True)
    answer = fields.String(required=True)

    @validates("question")
    def validate_question(self, question):
        if FrequentQuestion.check_frequent_question_exists(question):
            raise ValidationError("Frequent question đã tồn tại")

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["question"] = data["question"].lower().strip()
        data["answer"] = data["answer"].lower().strip()
        return data


class CreateSubjectValidation(Schema):
    """
    Validator
    """
    name = fields.String(required=True)
    code = fields.String(required=False)
    number_of_credit = fields.Integer(required=False)

    @validates("name")
    def validate_name(self, value):
        if Subject.check_subject_name_exists(value):
            raise ValidationError("Name đã tồn tại")

    @validates("code")
    def validate_code(self, value):
        if Subject.check_subject_code_exists(value):
            raise ValidationError("Code đã tồn tại")

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].lower().strip()
        data["code"] = data["code"].lower().strip() if data["code"] else None
        return data


class UpdateGroupValidation(Schema):
    """
    Validator
    """
    id = fields.String(required=False)
    name = fields.String(required=True)
    description = fields.String(required=False)
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


class UpdateStatusQuestionValidation(Schema):
    status = fields.Integer(required=True)


class UpdateAssigneeQuestionValidation(Schema):
    assignee_user_id = fields.String(required=True)


class UpdateQuestionValidation(Schema):
    id = fields.String(required=False)
    description = fields.String(required=False)
    title = fields.String(required=False)
    attached_file_url = fields.String(required=False)
    topic_id = fields.String(required=False)
    user_id = fields.String(required=True)
    assignee_user_id = fields.String(required=True)

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["title"] = data["title"].strip() if data["title"] else None
        data["description"] = data["description"].strip() if data["description"] else None
        return data

    @validates_schema
    def validate_name(self, data, **kwargs):
        if Question.check_question_exists(data["title"], data["id"]):
            raise ValidationError('Question đã tồn tại')


class UpdateTopicValidation(Schema):
    """
    Validator
    """
    id = fields.String(required=False)
    name = fields.String(required=True)
    description = fields.String(required=False)

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].strip()
        data["description"] = data["description"].strip() if data["description"] else None
        return data

    @validates_schema
    def validate_name(self, data, **kwargs):
        if TopicQuestion.check_topic_exists(data["name"], data["id"]):
            raise ValidationError('Topic đã tồn tại')


class UpdateFormValidation(Schema):
    """
    Validator
    """
    id = fields.String(required=False)
    name = fields.String(required=True)
    description = fields.String(required=False)
    link = fields.String(required=True)

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].strip()
        data["description"] = data["description"].strip() if data["description"] else None
        return data

    @validates_schema
    def validate_name(self, data, **kwargs):
        if Form.check_form_exists(data["name"], data["id"]):
            raise ValidationError('Topic đã tồn tại')


class UpdateFrequentQuestionValidation(Schema):
    """
    Validator
    """
    id = fields.String(required=False)
    question = fields.String(required=True)
    answer = fields.String(required=True)

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["question"] = data["question"].strip()
        data["answer"] = data["answer"].strip() if data["answer"] else None
        return data

    @validates_schema
    def validate_question(self, data, **kwargs):
        if FrequentQuestion.check_frequent_question_exists(data["question"], data["id"]):
            raise ValidationError('Frequent question đã tồn tại')


class UpdateSubjectValidation(Schema):
    """
    Validator
    """
    id = fields.String(required=False)
    name = fields.String(required=True)
    code = fields.String(required=False)
    number_of_credit = fields.Integer(required=False)

    # Clean up data
    @pre_load
    def process_input(self, data, **kwargs):
        data["name"] = data["name"].strip()
        data["code"] = data["code"].strip() if data["code"] else None
        return data

    @validates_schema
    def validate_name(self, data, **kwargs):
        if Subject.check_subject_name_exists(data["name"], data["id"]):
            raise ValidationError('Name đã tồn tại')
        if Subject.check_subject_code_exists(data["code"], data["id"]):
            raise ValidationError('Code đã tồn tại')


class GroupSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    name = fields.String()
    description = fields.String()
    creator_id = fields.String(required=False)
    creator = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))
    roles = fields.List(fields.Nested(RoleSchema(only=['id', 'name'])))


class FrequentQuestionSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    question = fields.String()
    answer = fields.String()
    creator_id = fields.String(required=False)
    creator = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))


class SubjectSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    name = fields.String()
    code = fields.String()
    number_of_credit = fields.Integer()
    creator_id = fields.String(required=False)
    creator = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))


class TopicSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    name = fields.String()
    description = fields.String()
    creator_id = fields.String(required=False)
    creator = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))
    number_of_questions = fields.Integer()


class StatisticTopicSchema(Schema):
    """
    Validator
    """
    name = fields.String()
    number_of_questions = fields.Integer()


class QuestionSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    description = fields.String()
    title = fields.String()
    created_date = fields.Integer()
    attached_file_url = fields.String()
    topic_id = fields.String()
    status = fields.Integer()
    user_id = fields.String()
    assignee_user_id = fields.String()
    creator_id = fields.String(required=False)
    creator = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))
    assignee_user = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))
    user = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))
    topic = fields.Nested(TopicSchema())


class CommentSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    message = fields.String()
    attached_file_url = fields.String()
    created_date = fields.Integer()
    sender_id = fields.String()
    question_id = fields.String()
    sender = fields.Nested(UserSchema())


class HistorySchema(Schema):
    """
    Validator
    """
    id = fields.String()
    status = fields.Integer()
    created_date = fields.Integer()
    creator_id = fields.String()
    assignee_user_id = fields.String()
    question_id = fields.String()
    creator = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))
    assignee_user = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))


class FormSchema(Schema):
    """
    Validator
    """
    id = fields.String()
    name = fields.String()
    description = fields.String()
    link = fields.String()
    creator_id = fields.String(required=False)
    creator = fields.Nested(UserSchema(only=['id', 'email', "first_name", "last_name", "avatar_url"]))


class GetTopicValidation(Schema):
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


class GetQuestionValidation(Schema):
    """
    """
    page = fields.Integer(required=False)
    page_size = fields.Integer(required=False)
    from_date = fields.Integer(required=False)
    to_date = fields.Integer(required=False)
    search_name = fields.String(required=False)
    status = fields.String(required=False)

    sort_by = fields.String(required=False,
                            validate=validate.OneOf(
                                ["title", "created_date", "modified_date"]))
    order_by = fields.String(required=False, validate=validate.OneOf(["asc", "desc"]))


class GetQuestionDetailValidation(Schema):
    """
    """
    page = fields.Integer(required=False)
    page_size = fields.Integer(required=False)


class GetFormValidation(Schema):
    """
    """
    page = fields.Integer(required=False)
    page_size = fields.Integer(required=False)
    search_name = fields.String(required=False)

    sort_by = fields.String(required=False,
                            validate=validate.OneOf(
                                ["name", "created_date", "modified_date"]))
    order_by = fields.String(required=False, validate=validate.OneOf(["asc", "desc"]))


class GetFrequentQuestionValidation(Schema):
    """
    """
    page = fields.Integer(required=False)
    page_size = fields.Integer(required=False)
    from_date = fields.Integer(required=False)
    to_date = fields.Integer(required=False)
    search_name = fields.String(required=False)

    sort_by = fields.String(required=False,
                            validate=validate.OneOf(
                                ["question", "answer", "created_date", "modified_date"]))
    order_by = fields.String(required=False, validate=validate.OneOf(["asc", "desc"]))


class GetStatisticQuestionValidation(Schema):
    from_date = fields.String(required=False)
    to_date = fields.String(required=False)


class GetSubjectValidation(Schema):
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


# Upload file

class UploadValidation(Schema):
    """
    Validator
    Ex:
    {
        "file_name": "default_avatars.png",
        "prefix": "avatars"
    }
    """
    file_name = fields.String(required=False, validate=validate.Length(min=1, max=50))
    prefix = fields.String(required=True)
