# coding=utf-8
from flask import Flask
from flasgger import Swagger


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config['SWAGGER'] = {"swagger": "2.0",
                             "title": "Yummy Recipes",
                             "uiversion": 2,
                             "info": {
                                "title": "Yummy Recipe API",
                                "description": "Yummy Recipe api challenge for is part of the boot-camp challenges."
                                      "\n\nThe link for the heroku app is 'https://api-yummy.herokuapp.com'."
                                      "\n\nThe github repo link is 'https://github.com/kevinsamoei/Yummy_Recipes_Api'",
                                "version": "1.0.0",
                                "basepath": '/',
                             },
                             "securityDefinitions": {
                                "TokenHeader": {
                                    "type": "apiKey",
                                    "name": "x-access-token",
                                    "in": "header"
                                },
                             },
                             "consumes": [
                                 "application/json",
                             ],
                             "produces": [
                                 "application/json",
                       ], }

    Swagger(app)

    from models import db
    db.init_app(app)

    from api.endpoints import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
