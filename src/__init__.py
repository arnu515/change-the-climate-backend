from flask import Flask, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, MethodNotAllowed
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(os.path.join(os.path.dirname(__file__), "config.py"))
    CORS(app)
    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        db.create_all()

        # Routes
        from .routes import auth
        from .routes import posts
        from .routes import comments
        from .routes import users

        app.register_blueprint(auth.b)
        app.register_blueprint(posts.b)
        app.register_blueprint(comments.b)
        app.register_blueprint(users.b)

        # Exceptions
        from .routes import HTTPException

        @app.errorhandler(BadRequest)
        def bad_req_eh(e: BadRequest):
            return make_response(jsonify(dict(success=False, message=e.description, data=dict())), e.code)

        @app.errorhandler(MethodNotAllowed)
        def bad_req_eh(e: MethodNotAllowed):
            return make_response(jsonify(dict(success=False, message=e.description, data=dict())), e.code)

        @app.errorhandler(InternalServerError)
        def int_server_eh(e: InternalServerError):
            return make_response(jsonify(dict(success=False, message=e.description, data=dict())), e.code)

        @app.errorhandler(NotFound)
        def not_found_eh(e: NotFound):
            return make_response(jsonify(dict(success=False, message=e.description, data=dict())), e.code)

        @app.errorhandler(HTTPException)
        def http_ex_eh(e: HTTPException):
            return e.response

        return app
