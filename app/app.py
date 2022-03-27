# -*- coding: utf-8 -*-
import traceback
from time import strftime
from flask import Flask, request, jsonify
from app.extensions import jwt
from app.api import v1 as api_v1
from app.extensions import logger, parser, db
from .enums import TIME_FORMAT_LOG, FAIL
from .settings import ProdConfig
from app.api.helper import send_error, send_result
from flask_cors import CORS


def create_app(config_object=ProdConfig):
    """Init App Register Application extensions and API prefix

    Args:
        config_object: We will use Prod Config when the environment variable has FLASK_DEBUG=1.
        You can run export FLASK_DEBUG=1 in order to run in application dev mode.
        You can see config_object in the settings.py file
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app, config_object)
    register_blueprints(app)
    register_monitor(app)
    CORS(app)
    return app


def register_extensions(app, config_object):
    """Init extension. You can see list extension in the extensions.py

    Args:
        app: Flask handler application
        config_object: settings of the application
        :param
    """
    # Order matters: Initialize SQLAlchemy before Marshmallow
    # create log folder
    db.app = app
    jwt.init_app(app)
    db.init_app(app)

    @app.after_request
    def after_request(response):
        # This IF avoids the duplication of registry in the log,
        # since that 500 is already logged via @app.errorhandler.
        if 200 <= response.status_code < 400:
            ts = strftime('[%Y-%b-%d %H:%M]')
            logger.info('%s %s %s %s %s %s',
                        ts,
                        request.remote_addr,
                        request.method,
                        request.scheme,
                        request.full_path,
                        response.status)

        return response

    @app.errorhandler(Exception)
    def exceptions(e):
        """
        Handling exceptions
        :param e:
        :return:
        """
        ts = strftime(TIME_FORMAT_LOG)
        error = '{} {} {} {} {} {}'.format(ts, request.remote_addr, request.method, request.scheme, request.full_path,
                                           str(e))
        logger.error(error)
        code = 500
        if hasattr(e, 'code'):
            code = e.code

        return send_error(message=str(e), code=code)

    @parser.error_handler
    def handle_error(error, req, schema, *, error_status_code, error_headers):
        return send_error(message='Parser error. Please check your requests body', code=500, message_id=FAIL)

    # # Return validation errors as JSON
    # @app.errorhandler(422)
    # @app.errorhandler(400)
    # def handle_error(err):
    #     headers = err.data.get("headers", None)
    #     messages = err.data.get("messages", ["Invalid request."])
    #     if headers:
    #         return jsonify({"errors": messages}), err.code, headers
    #     else:
    #         return jsonify({"errors": messages}), err.code


def register_monitor(app):
    def has_no_empty_params(rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    @app.route("/api/v1/helper/site-map", methods=['GET'])
    def site_map():
        links = []
        for rule in app.url_map.iter_rules():
            # Filter out rules we can't navigate to in a browser
            # and rules that require parameters
            # if has_no_empty_params(rule):
            # url = url_for(rule.endpoint, **(rule.defaults or {}))
            request_method = ""
            if "GET" in rule.methods:
                request_method = "get"
            if "PUT" in rule.methods:
                request_method = "put"
            if "POST" in rule.methods:
                request_method = "post"
            if "DELETE" in rule.methods:
                request_method = "delete"
            permission_route = "{0}@{1}".format(request_method.lower(), rule)
            links.append(permission_route)
        return send_result(data=sorted(links, key=lambda resource: str(resource).split('@')[-1]))


def register_blueprints(app):
    """Init blueprint for api url
    :param app: Flask application
    """
    app.register_blueprint(api_v1.auth.api, url_prefix='/api/v1/admin/auth')
    app.register_blueprint(api_v1.user.api, url_prefix='/api/v1/admin/users')
    app.register_blueprint(api_v1.role.api, url_prefix='/api/v1/admin/roles')
    app.register_blueprint(api_v1.permission.api, url_prefix='/api/v1/admin/permissions')
    app.register_blueprint(api_v1.group.api, url_prefix='/api/v1/admin/groups')
    app.register_blueprint(api_v1.topic_question.api, url_prefix='/api/v1/admin/topics')
    app.register_blueprint(api_v1.subject.api, url_prefix='/api/v1/admin/subjects')
    app.register_blueprint(api_v1.frequent_question.api, url_prefix='/api/v1/admin/frequent_questions')
