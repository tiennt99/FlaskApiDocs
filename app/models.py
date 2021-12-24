# coding: utf-8
import uuid

from flask_jwt_extended import decode_token, get_raw_jwt
from sqlalchemy import Column, ForeignKey, String, Boolean, SmallInteger, TEXT
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy import or_, and_

from app.extensions import db
from app.utils import get_timestamp_now

Base = db.Model
session = db.session


def close_session():
    session.close()


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
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    status = db.Column(db.String(50))
    type = db.Column(db.String(50))
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    group_id = db.Column(ForeignKey('group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                         index=True)

    group = relationship('Group', primaryjoin='User.group_id == Group.id')


class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    resource = db.Column(db.String(500), nullable=False, unique=True)


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.String(50), primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    type = db.Column(db.SmallInteger, default=1)  # tổng của 4 loại quyền sau 1: Xem, 2: Thêm, 4: Sửa, 8: Xóa
    is_show = db.Column(db.Boolean, default=1)


class RolePermission(db.Model):
    __tablename__ = 'role_permission'

    id = db.Column(db.String(50), primary_key=True)
    role_id = db.Column(ForeignKey('role.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    permission_id = db.Column(ForeignKey('permission.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                              index=True)

    permission = relationship('Permission', primaryjoin='RolePermission.permission_id == Permission.id')
    role = relationship('Role', primaryjoin='RolePermission.role_id == Role.id')


class GroupRole(db.Model):
    __tablename__ = 'group_role'

    id = db.Column(db.String(50), primary_key=True)
    role_id = db.Column(ForeignKey('role.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    group_id = db.Column(ForeignKey('group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

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
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now(), index=True)
    modified_date = db.Column(INTEGER(unsigned=True), default=0)

    @classmethod
    def get_by_id(cls, _id):
        return cls.query.get(_id)

    group_roles = relationship('GroupRole', primaryjoin='GroupRole.group_id == Group.id')

    @property
    def roles(self):
        return [gr.role for gr in self.group_roles]
