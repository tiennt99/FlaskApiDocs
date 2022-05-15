import os
import json
import uuid

from flask import Flask
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User, Message, Group, Role, GroupRole, Permission, RolePermission, TopicQuestion, \
    FrequentQuestion, Subject, Question, Form, Comment, History, Class, ClassUser
from app.settings import ProdConfig, DevConfig


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

        with open('data/topic_question.json', encoding='utf-8') as file:
            self.topic_question = json.load(file)
        with open('data/frequent_question.json', encoding='utf-8') as file:
            self.frequent_question = json.load(file)
        with open('data/subject.json', encoding='utf-8') as file:
            self.subject = json.load(file)
        with open('data/form.json', encoding='utf-8') as file:
            self.form = json.load(file)
        with open('data/question.json', encoding='utf-8') as file:
            self.question = json.load(file)
        with open('data/comment.json', encoding='utf-8') as file:
            self.comment = json.load(file)
        with open('data/history.json', encoding='utf-8') as file:
            self.history = json.load(file)
        with open('data/class.json', encoding='utf-8') as file:
            self._class = json.load(file)
        with open('data/class_user.json', encoding='utf-8') as file:
            self._class_user = json.load(file)

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

    def create_default_user(self):
        users = self.default_user
        for item in users:
            instance = User()
            for key in item.keys():
                instance.__setattr__(key, item[key])

            instance.password_hash = generate_password_hash(instance.password)
            db.session.add(instance)
        db.session.commit()

    def create_default_user_example(self):
        users = self.default_user_example
        for item in users:
            instance = User()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            instance.password_hash = generate_password_hash(instance.password)
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

    def create_default_topic_question(self):
        topic_questions = self.topic_question
        for item in topic_questions:
            instance = TopicQuestion()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_frequent_question(self):
        frequent_questions = self.frequent_question
        for item in frequent_questions:
            instance = FrequentQuestion()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_subject(self):
        subjects = self.subject
        for item in subjects:
            instance = Subject()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_question(self):
        questions = self.question
        for item in questions:
            instance = Question()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_form(self):
        forms = self.form
        for item in forms:
            instance = Form()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_comment(self):
        comments = self.comment
        for item in comments:
            instance = Comment()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_history(self):
        histories = self.history
        for item in histories:
            instance = History()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_class(self):
        _classes = self._class
        for item in _classes:
            instance = Class()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)
        db.session.commit()

    def create_default_class_user(self):
        _class_user = self._class_user
        for item in _class_user:
            instance = ClassUser()
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
    # worker.create_default_user()
    worker.create_default_user_example()
    # Topic question default
    worker.create_default_topic_question()
    # Frequent question default
    worker.create_default_frequent_question()
    # Subject default
    worker.create_default_subject()

    # form default
    worker.create_default_form()
    # question default
    worker.create_default_question()
    # comment default
    worker.create_default_comment()
    # history default
    worker.create_default_history()
    # class default
    # worker.create_default_class()
    # worker.create_default_class_user()
    print("=" * 50, "Database Migrate Completed", "=" * 50)
