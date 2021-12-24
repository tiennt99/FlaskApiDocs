import os
import json
import uuid

from flask import Flask

from app.extensions import db
from app.models import User, Message, Group
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
        with open('data/user.json', encoding='utf-8') as file:
            self.default_user = json.load(file)
        with open('data/message.json', encoding='utf-8') as file:
            self.default_message = json.load(file)

    def create_default_group(self):
        groups = self.default_group
        for item in groups:
            instance = Group()
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
    worker.create_default_group()
    worker.create_default_user()
    worker.create_default_message()
    print("=" * 50, "Database Migrate Completed", "=" * 50)
