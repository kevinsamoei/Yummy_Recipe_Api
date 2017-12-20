# coding=utf-8
from flask import Flask
from flasgger import Swagger
from api.auth import token_required

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config["Swagger"] = {
        "title": "Yummy Recipe App",
        "uiversion": 2,
    }
    swag = Swagger(app,
                   template={
                       "swagger": "2.0",
                       "info": {
                           "title": "Yummy Recipe API",
                           "version": "1.0",
                       },
                       "securityDefinitions": {
                           "TokenHeader": {
                               "type": "apiKey",
                               "name": "x-access-token",
                               "in": "header"
                           },
                           'basicAuth': {'type': 'basic'}
                       },
                       "consumes": [
                           "application/json",
                       ],
                       "produces": [
                           "application/json",
                       ],
                   },
                   )

    from models import db
    db.init_app(app)

    from api.endpoints import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
