import os
import json
import uuid

from flask import Flask

from app.extensions import db
from app.models import User, Message, Group, Role, GroupRole, Permission, RolePermission
from app.settings import ProdConfig, DevConfig
from app.utils import password_encode


class Worker:
    """
    Drop all tables. Load default data from user.json and insert into new database
    """

    def __init__(self):
        print("=" * 50, "Starting migrate database", "=" * 50)
        config = DevConfig if os.environ.get('FLASK_DEBUG') == '1' else ProdConfig

        app = Flask(__name__)
        app.config.from_object(config)
        db.app = app
        db.init_app(app)

        print(f"Starting migrate database on the uri: {config.SQLALCHEMY_DATABASE_URI}")
        app_context = app.app_context()
        app_context.push()
        db.drop_all()  # drop all tables
        db.create_all()  # create a new schema
        with open('data/group.json', encoding='utf-8') as file:
            self.default_group = json.load(file)
        with open('data/group_role.json', encoding='utf-8') as file:
            self.default_group_role = json.load(file)
        with open('data/role.json', encoding='utf-8') as file:
            self.default_role = json.load(file)
        with open('data/permission.json', encoding='utf-8') as file:
            self.default_permission = json.load(file)
        with open('data/user.json', encoding='utf-8') as file:
            self.default_user = json.load(file)
        with open('data/user_default.json', encoding='utf-8') as file:
            self.default_user_example = json.load(file)
        with open('data/message.json', encoding='utf-8') as file:
            self.default_message = json.load(file)

    def create_default_group(self):
        groups = self.default_group
        for item in groups:
            role_ids = item["role_ids"]
            instance = Group()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            group_id = instance.id
            db.session.add(instance)
            for role_id in role_ids:
                group_role = GroupRole(id=str(uuid.uuid4()),
                                       group_id=group_id,
                                       role_id=role_id)
                db.session.add(group_role)
        db.session.commit()

    def create_default_role(self):
        roles = self.default_role
        for item in roles:
            permission_ids = item["permission_ids"]
            instance = Role()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            role_id = instance.id
            db.session.add(instance)
            # add roles
            for permission_id in permission_ids:
                role_permission = RolePermission(id=str(uuid.uuid4()),
                                                 role_id=role_id,
                                                 permission_id=permission_id)
                db.session.add(role_permission)
        db.session.commit()

    def create_default_permission(self):
        permissions = self.default_permission
        for item in permissions:
            instance = Permission()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_group_role(self):
        group_roles = self.default_group_role
        for item in group_roles:
            instance = GroupRole()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_user(self):
        users = self.default_user
        for item in users:
            instance = User()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            instance.password = password_encode(instance.password)
            db.session.add(instance)
        db.session.commit()

    def create_default_user_example(self):
        users = self.default_user_example
        for item in users:
            instance = User()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            instance.password = password_encode(instance.password)
            db.session.add(instance)
        db.session.commit()

    def create_default_message(self):
        messages = self.default_message
        for item in messages:
            instance = Message()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()


if __name__ == '__main__':
    worker = Worker()
    # Message id
    worker.create_default_message()
    # Permission default
    worker.create_default_permission()
    # Role default
    worker.create_default_role()
    # Group admin, teacher, student
    worker.create_default_group()
    # User default
    worker.create_default_user()
    worker.create_default_user_example()

    print("=" * 50, "Database Migrate Completed", "=" * 50)
