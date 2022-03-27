# coding: utf-8
import uuid

from flask_jwt_extended import decode_token, get_raw_jwt
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy import or_, and_
from app.extensions import db
from app.utils import get_timestamp_now

Base = db.Model
session = db.session


def close_session():
    session.close()


# Start Phân Quyền
class Token(db.Model):
    __tablename__ = 'token'

    id = db.Column(db.String(50), primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(50), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(INTEGER(unsigned=True), nullable=False)

    @staticmethod
    def add_token_to_database(encoded_token, user_identity):
        """
        Adds a new token to the database. It is not revoked when it is added.
        :param encoded_token:
        :param user_identity:
        """
        decoded_token = decode_token(encoded_token)
        jti = decoded_token['jti']
        token_type = decoded_token['type']
        expires = decoded_token['exp']
        revoked = False
        _id = str(uuid.uuid1())

        db_token = Token(
            id=_id,
            jti=jti,
            token_type=token_type,
            user_identity=user_identity,
            expires=expires,
            revoked=revoked,
        )
        db.session.add(db_token)
        db.session.commit()

    @staticmethod
    def is_token_revoked(decoded_token):
        """
        Checks if the given token is revoked or not. Because we are adding all the
        token that we create into this database, if the token is not present
        in the database we are going to consider it revoked, as we don't know where
        it was created.
        """
        jti = decoded_token['jti']
        token = Token.query.filter_by(jti=jti).first()
        if token:
            return token.revoked
        return True

    @staticmethod
    def revoke_token(jti):
        """
        Revokes the given token. Raises a TokenNotFound error if the token does
        not exist in the database
        """
        try:
            token = Token.query.filter_by(jti=jti).first()
            token.revoked = True
            db.session.commit()
        except Exception as ex:
            return str(ex)

    @staticmethod
    def revoke_all_token(users_identity):
        """
        Revokes the given token. Raises a TokenNotFound error if the token does
        not exist in the database.
        Set token Revoked flag is False to revoke this token.
        Args:
            users_identity: list or string, require
                list user id or user_id. Used to query all token of the user on the database
        """
        try:
            if type(users_identity) is not list:
                # convert user_id to list user_ids
                users_identity = [users_identity]

            tokens = Token.query.filter(Token.user_identity.in_(users_identity), Token.revoked == 0).all()

            for token in tokens:
                token.revoked = True
            db.session.commit()
        except Exception as ex:
            return str(ex)

    @staticmethod
    def revoke_all_token2(users_identity):
        """
        Revokes all token of the given user except current token. Raises a TokenNotFound error if the token does
        not exist in the database.
        Set token Revoked flag is False to revoke this token.
        Args:
            users_identity: user id
        """
        jti = get_raw_jwt()['jti']
        try:
            tokens = Token.query.filter(Token.user_identity == users_identity, Token.revoked == 0,
                                        Token.jti != jti).all()
            for token in tokens:
                token.revoked = True
            db.session.commit()
        except Exception as ex:
            return str(ex)

    @staticmethod
    def prune_database():
        """
        Delete tokens that have expired from the database.
        How (and if) you call this is entirely up you. You could expose it to an
        endpoint that only administrators could call, you could run it as a cron,
        set it up with flask cli, etc.
        """
        now_in_seconds = get_timestamp_now()
        Token.query.filter(Token.expires < now_in_seconds).delete()
        db.session.commit()


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.String(50), primary_key=True)
    description = db.Column(db.String(255))
    show = db.Column(db.Boolean, nullable=0)
    duration = db.Column(db.Integer, default=5)
    status = db.Column(db.String(20), default='success')
    message = db.Column(db.String(255), nullable=False)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    status = db.Column(db.Boolean, default=1)
    creator_id = db.Column(db.String(50), default="8dbd546c-6497-11ec-90d6-0242ac120003")  # Default admin
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)
    group_id = db.Column(ForeignKey('group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True,
                         index=True)

    group = relationship('Group', primaryjoin='User.group_id == Group.id')

    @classmethod
    def get_user_by_id(cls, _id):
        return cls.query.get(_id)

    @classmethod
    def check_user_exists(cls, keyword: str, user_id: str = None):
        if user_id:
            return cls.query.filter(and_(cls.id != user_id, or_(cls.email == keyword, cls.username == keyword))).first()
        return cls.query.filter(or_(cls.email == keyword, cls.username == keyword)).first()


class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    resource = db.Column(db.String(500), nullable=False, unique=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    module = db.Column(db.String(100))
    description = db.Column(db.String(255))
    creator_id = db.Column(db.String(50), default="8dbd546c-6497-11ec-90d6-0242ac120003")  # Default admin
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    role_permissions = relationship('RolePermission', primaryjoin='Role.id == RolePermission.role_id')

    @classmethod
    def get_role_by_id(cls, _id):
        return cls.query.get(_id)

    @property
    def permissions(self):
        return [obj.permission for obj in self.role_permissions]

    @classmethod
    def check_role_exists(cls, keyword: str, role_id: str = None):
        if role_id:
            return cls.query.filter(and_(cls.id != role_id, cls.name == keyword)).first()
        return cls.query.filter(cls.name == keyword).first()


class RolePermission(db.Model):
    __tablename__ = 'role_permission'

    id = db.Column(db.String(50), primary_key=True)
    role_id = db.Column(ForeignKey('role.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    permission_id = db.Column(ForeignKey('permission.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                              index=True)
    role_accessibility = db.Column(db.SmallInteger, default=0)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)
    creator_id = db.Column(db.String(50), default="8dbd546c-6497-11ec-90d6-0242ac120003")  # Default admin

    permission = relationship('Permission', primaryjoin='RolePermission.permission_id == Permission.id')
    # role = relationship('Role', primaryjoin='RolePermission.role_id == Role.id')


class GroupRole(db.Model):
    __tablename__ = 'group_role'

    id = db.Column(db.String(50), primary_key=True)
    role_id = db.Column(ForeignKey('role.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    group_id = db.Column(ForeignKey('group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)
    creator_id = db.Column(db.String(50), default="8dbd546c-6497-11ec-90d6-0242ac120003")  # Default admin

    # group = relationship('Group', primaryjoin='GroupRole.group_id == Group.id')
    role = relationship('Role', primaryjoin='GroupRole.role_id == Role.id')

    @classmethod
    def get_by_id(cls, _id):
        return cls.query.get(_id)


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    creator_id = db.Column(db.String(50), default="8dbd546c-6497-11ec-90d6-0242ac120003")  # Default admin
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)
    group_roles = relationship('GroupRole', primaryjoin='Group.id == GroupRole.group_id')

    @property
    def creator(self):
        return User.get_user_by_id(self.creator_id)

    @property
    def roles(self):
        return [obj.role for obj in self.group_roles]

    @classmethod
    def get_group_by_id(cls, _id):
        return cls.query.get(_id)

    @classmethod
    def check_group_exists(cls, keyword: str, group_id: str = None):
        if group_id:
            return cls.query.filter(and_(cls.id != group_id, cls.name == keyword)).first()
        return cls.query.filter(cls.name == keyword).first()


# End phân quyền
# Start quản lý tiếp đón
class TopicQuestion(db.Model):
    __tablename__ = 'topic_question'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    creator_id = db.Column(db.String(50), default="8dbd546c-6497-11ec-90d6-0242ac120003")  # Default admin
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)

    @classmethod
    def get_topic_by_id(cls, _id):
        return cls.query.get(_id)

    @classmethod
    def check_topic_exists(cls, name: str, topic_id: str = None):
        if topic_id:
            return cls.query.filter(and_(cls.id != topic_id, cls.name == name)).first()
        return cls.query.filter(cls.name == name).first()


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.String(50), primary_key=True)
    start_time = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    end_time = db.Column(INTEGER(unsigned=True), default=get_timestamp_now() + 1800)  # Default + 30 phút
    description = db.Column(db.String(255))
    content = db.Column(db.String(255))
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)
    attached_file = db.Column(db.String(255))
    creator_id = db.Column(db.String(50), default="8dbd546c-6497-11ec-90d6-0242ac120003")  # Default admin
    user_id = db.Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    topic_id = db.Column(ForeignKey('topic_question.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                         index=True)
    topic = relationship('TopicQuestion', primaryjoin='Question.topic_id == TopicQuestion.id')
    user = relationship('User', primaryjoin='Question.user_id == User.id')


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.String(50), primary_key=True)
    status = db.Column(db.SmallInteger, default=0)  # 1 - Đang xử lý, 2 - Chờ xử lý , 3- Xử lý xong
    note = db.Column(db.String(255))
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)
    user_id = db.Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                        index=True)
    question_id = db.Column(ForeignKey('question.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                            index=True)
    question = relationship('Question', primaryjoin='History.question_id == Question.id')
    user = relationship('User', primaryjoin='History.user_id == User.id')


# End quản lý tiếp đón
# Start Quan Tri sinh vien giao vien
# TODO: Cập nhập đầy đủ sau
class UserDetail(db.Model):
    __tablename__ = 'user_detail'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50))
    student_code = db.Column(db.String(50))
    birth_day = db.Column(INTEGER(unsigned=True), default=0)
    is_card = db.Column(db.Boolean)
    is_priority = db.Column(db.Boolean)
    folk = db.Column(db.String(50))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    file_number = db.Column(db.String(50))
    sex = db.Column(db.String(50))
    status_question = db.Column(db.SmallInteger, default=0)  # 0 - Đang xử lý, 1 - Xử lý xong
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)


# End Quan Tri sinh vien giao vien

# Start chat message
class GroupChat(db.Model):
    __tablename__ = 'group_chat'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50))
    avatar = db.Column(db.String(500))
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)


class GroupChatUser(db.Model):
    __tablename__ = 'group_chat_user'

    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                        index=True)
    group_chat_id = db.Column(ForeignKey('group_chat.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                              index=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)


class ChatMessage(db.Model):
    __tablename__ = 'chat_message'

    id = db.Column(db.String(50), primary_key=True)
    message = db.Column(db.TEXT)
    sender_id = db.Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                          index=True)
    group_chat_id = db.Column(ForeignKey('group_chat.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                              index=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)


# End chat message

# Start Frequently asked questions
class FrequentQuestion(db.Model):
    __tablename__ = 'frequent_question'

    id = db.Column(db.String(50), primary_key=True)
    question = db.Column(db.TEXT)
    answer = db.Column(db.TEXT)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)
    creator_id = db.Column(db.String(50), default="8dbd546c-6497-11ec-90d6-0242ac120003")  # Default admin

    @classmethod
    def check_frequent_question_exists(cls, question: str, frequent_question_id: str = None):
        if frequent_question_id:
            return cls.query.filter(and_(cls.id != frequent_question_id, cls.question == question)).first()
        return cls.query.filter(cls.question == question).first()

    @classmethod
    def get_frequent_question_by_id(cls, _id):
        return cls.query.get(_id)


# End Frequently asked questions
# Start Subject score
class Subject(db.Model):
    __tablename__ = 'subject'

    id = db.Column(db.String(50), primary_key=True)
    code = db.Column(db.String(10))
    name = db.Column(db.String(50))
    number_of_credit = db.Column(db.SmallInteger)

    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)

    @classmethod
    def get_subject_by_id(cls, _id):
        return cls.query.get(_id)

    @classmethod
    def check_subject_name_exists(cls, name: str, subject_id: str = None):
        if subject_id:
            return cls.query.filter(and_(cls.id != subject_id, cls.name == name)).first()
        return cls.query.filter(cls.name == name).first()

    @classmethod
    def check_subject_code_exists(cls, code: str, subject_id: str = None):
        if subject_id:
            return cls.query.filter(and_(cls.id != subject_id, cls.code == code)).first()
        return cls.query.filter(cls.code == code).first()


class UserSubject(db.Model):
    __tablename__ = 'user_subject'

    id = db.Column(db.String(50), primary_key=True)
    attendance_score = db.Column(db.Float)
    regular_score = db.Column(db.Float)
    final_exam_score = db.Column(db.Float)
    final_grade = db.Column(db.Float)
    user_id = db.Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                        index=True)
    subject_id = db.Column(ForeignKey('subject.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                           index=True)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)
# End Subject score
