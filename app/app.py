import os
from flask import Flask, g, redirect, url_for

from api import api
import time

from .extensions import influx_db, auth



BLUEPRINTS = (
    api,
)


def create_app(config=None, app_name=None,):
    """Create a Flask app."""

    if app_name is None:
        app_name = __name__


    app = Flask(app_name)

    app.config.from_object(config)


    app.secret_key = app.config['SECRET_KEY']

    # Extensions that must init with .init_app(app)
    influx_db.init_app(app)

    configure_blueprints(app, BLUEPRINTS)

    @app.before_first_request
    def create_influx_db():
        influx_db.connection.create_database(app.config['INFLUXDB_DATABASE'],
                                             if_not_exists=True)

    @auth.verify_password
    def verify_password(api_key, _):
        return api_key == app.config['API_KEY']

    return app


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
