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
                                "description": "Yummy recipes provides a platform for users to keep track of their "
                                               "awesome recipes and share with others if they so wish."
                                      "\n\nThe link for the heroku app is 'https://yummyrecipesapi.herokuapp.com'."
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

    from api.models import db
    db.init_app(app)

    from api.endpoints.recipes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    from api.endpoints.user import api_bp
    app.register_blueprint(api_bp,url_prefix='/api/auth')
    from api.endpoints.categories import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/categories')
    return app
