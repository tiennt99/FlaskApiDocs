import os
import json
import uuid

from flask import Flask

from app.extensions import db
from app.models import Users, Message
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

        with open('user.json', encoding='utf-8') as file:
            self.default_users = json.load(file)
        with open('message.json', encoding='utf-8') as file:
            self.default_data = json.load(file)

    def create_default_users(self):
        users = self.default_users
        for item in users:
            instance = Users()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)

        db.session.commit()

    def create_default_message(self):
        messages = self.default_data
        for item in messages:
            instance = Message()
            for key in item.keys():
                instance.__setattr__(key, item[key])
            db.session.add(instance)

        db.session.commit()


if __name__ == '__main__':
    worker = Worker()
    worker.create_default_users()
    worker.create_default_message()
    print("=" * 50, "Database Migrate Completed", "=" * 50)
