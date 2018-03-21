import datetime
import jwt
import re
import os
import random
import string

from flask import Blueprint, request, jsonify, make_response, abort, Flask
from flask_restful import Api, Resource
from flask_mail import Message, Mail
from passlib.apps import custom_app_context as password_context


from api.models import db, User, DisableTokens
from api.serializers import UserSchema

from api import status
from api.auth import token_required
from api.validate_json import validate_json


app = Flask(__name__)

api_bp = Blueprint('api/auth', __name__)

app_context = app.app_context()
app_context.push()

user_schema = UserSchema()
api = Api(api_bp)

app.config.update(
    DEBUG=True,
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
)
mail = Mail(app)


class RegisterUser(Resource):
    """"
    Class to register a new user
    """
    @validate_json
    def post(self):
        """
         Register a user
        ---
        tags:
          - auth
        parameters:
          - in: body
            name: body
            required: true
            description: User's name and password
            schema:
              id: register
              properties:
                username:
                  type: string
                  default: kevin
                password:
                  type: string
                  default: P@ssword1
                email:
                  type: string
                  default: samoeikev@gmail.com
        responses:
          200:
            description: A registered user
            schema:
              id: user
              properties:
                username:
                  type: string
                  default: kevin
                password:
                  type: string
                  default: P@ssword1
                email:
                  type: string
                  default: samoeikev@gmail.com
        """
        request_dict = request.get_json()
        if not request_dict:
            response = {'error': 'No input data provided'}
            abort(status.HTTP_400_BAD_REQUEST, response)
        errors = user_schema.validate(request_dict)
        if errors:
            abort(status.HTTP_400_BAD_REQUEST, errors)
        try:
            username = request_dict['username'].lower()
            if re.match(r'[A-Za-z]+$', username) is None:
                return {"error": "Non-alphabetic characters for username are not allowed"}, 400
            password = request_dict['password']
            email = request_dict['email']
        except KeyError as error:
            res = {"error": str(error)}
            abort(400, res)
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            abort(409, {"error": "A user with the same email already exists"})
        if not User.is_unique(username=username):
            response = {"error": "A user with the same name already exists"}
            abort(status.HTTP_409_CONFLICT, response)
        error, validated_name = User.validate_data(ctx=username)
        if validated_name:
            user = User(username=username, email=email)
            error_message, password_ok = \
                user.check_password_strength_and_hash_if_ok(password)
            if password_ok:
                user.add(user)
                result = {"message": "User successfully registered"}
                return result, status.HTTP_201_CREATED
            else:
                res = {'error': error_message}
                abort(status.HTTP_400_BAD_REQUEST, res)
        else:
            response = {"error": error}
            abort(response, 400)


class LoginUser(Resource):
    """
    Defines methods for manipulating a single user
    """
    @validate_json
    def post(self):
        """
        Log in a user and get a token
        ---
        tags:
          - auth
        parameters:
          - in: body
            name: body
            required: true
            description: The user's details
            type: string
            schema:
              id: user
              properties:
                username:
                  type: string
                  default: kevin
                password:
                  type: string
                  default: P@ssword1
        responses:
          200:
            description: A token for the user
            schema:
              id: user
              properties:
                username:
                  type: string
                  default: kevin
                password:
                  type: string
                  default: P@ssword1

                """
        auth = request.get_json()
        try:
            if not auth or not auth['username'] or not auth['password']:
                abort(status.HTTP_400_BAD_REQUEST, 'All fields are required')
        except KeyError as e:
            abort(status.HTTP_400_BAD_REQUEST, str(e))

        user = User.query.filter_by(username=auth['username']).first()

        if not user:
            return {'error': 'No user with that name exists'}, 400

        if user.verify_password(auth['password']):
            token = jwt.encode(
                {'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
                'topsecret')

            return jsonify({"token": token.decode('UTF-8'), "username": user.username})

        return {'error': 'Could not verify. Wrong password'}, 401


class LogoutUser(Resource):
    """
    Defines methods for the Logout Resource
    """
    @token_required
    def post(current, self):
        """
                Logout a user
                ---
                tags:
                  - auth
                responses:
                  200:
                    description: A user has been successfully logged out

                        """
        # Get the auth token
        token = request.headers['x-access-token']
        if token:
            disable_token = DisableTokens(token=token)
            db.session.add(disable_token)
            db.session.commit()
            return make_response(jsonify({"Message": "Successfully logged out"}), 200)


class SendResetPassword(Resource):
    """
    Resource to reset a user's password
    """
    @validate_json
    def post(self):
        """Reset a user's password
        ---
        tags:
          - auth
        parameters:
          - in: body
            name: body
            description: Old password and new user password
            type: string
            schema:
              id: change-password
              properties:
                username:
                  default: kevin
                email:
                  default: samoeikev@gmail.com
        responses:
          201:
            description: successfully changed the password
          400:
            description: Bad request. Wrong details, missing parameters and invalid passwords

        """

        request_dict = request.get_json()

        if not request_dict:
            resp = {'error': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST

        try:
            email = request_dict['email']
        except Exception:
            response = {"error": 'Missing field'}
            return response, status.HTTP_400_BAD_REQUEST

        user = User.query.filter_by(email=email).first()
        if not user:
            return {'error': "Invalid email"}, 400

        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits

        new_password = ''.join(random.choice(chars) for i in range(8))
        user.hashed_password = password_context.encrypt(new_password)

        user.update()

        try:
            msg = Message("Password Reset, Yummy Recipes",
                          sender="Admin",
                          recipients=[email])
            msg.html = "<h1>Hello," + user.username + "</h1>" \
                       "<p>Your password has been reset to: " + '<strong>' + new_password + '</strong>' + "</p>" \
                                                                            "<p> Make sure to change your password " \
                                                                             "on Login</p>" \
                                                                             "<p> \n\nCheers, Kevin Samoei </p>"
            with app_context:
                mail.send(msg)
            return {"message": 'Password Reset successful. Mail sent! Check email'}, 200
        except Exception as e:
            return {"error": str(e)}, 400


class ChangePassword(Resource):
    """
    Resource to reset a user's password
    """
    @validate_json
    @token_required
    def post(current_user, self):
        """Reset a user's password
        ---
        tags:
          - auth
        parameters:
          - in: body
            name: body
            description: Old password and new user password
            type: string
            schema:
              id: password
              properties:
                password:
                  default: P@ssword1
        responses:
          201:
            description: successfully changed the password
          400:
            description: Bad request. Wrong details, missing parameters and invalid passwords

        """

        request_dict = request.get_json()

        try:
            password = request_dict['new_password']
        except Exception as e:
            response = {"error": str(e)}
            return response, status.HTTP_400_BAD_REQUEST

        user = User.query.filter_by(id=current_user.id).first()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        error_message, password_ok = \
            user.check_password_strength_and_hash_if_ok(password)
        if password_ok:
                user.update()
                result = {"Message": "Password successfully changed!"}
                return result, status.HTTP_201_CREATED
        else:
            return {'error': error_message}, status.HTTP_400_BAD_REQUEST


api.add_resource(RegisterUser, '/register/')
api.add_resource(LoginUser, '/login/')
api.add_resource(LogoutUser, '/logout/')
api.add_resource(SendResetPassword, '/reset-password/')
api.add_resource(ChangePassword, '/change-password/')
