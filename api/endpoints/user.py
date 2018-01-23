import datetime
import jwt

from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource

from api.models import db, User, DisableTokens
from api.serializers import UserSchema

from api import status
from api.auth import token_required


api_bp = Blueprint('api/auth', __name__)
user_schema = UserSchema()
api = Api(api_bp)


class RegisterUser(Resource):
    """"
    Class to register a new user
    """
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
        """
        request_dict = request.get_json()
        if not request_dict:
            response = {'user': 'No input data provided'}
            return response, status.HTTP_400_BAD_REQUEST
        errors = user_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            username = request_dict['username'].lower()
            password = request_dict['password']
        except KeyError as error:
            return {"error": str(error)}, 400
        if not User.is_unique(username=username):
            response = {"error": "A user with the same name already exists"}
            return response, status.HTTP_400_BAD_REQUEST
        error, validated_name = User.validate_data(ctx=username)
        if validated_name:
            user = User(username=username)
            error_message, password_ok = \
                user.check_password_strength_and_hash_if_ok(password)
            if password_ok:
                user.add(user)
                query = User.query.get(user.id)
                result = user_schema.dump(query).data
                return result, status.HTTP_201_CREATED
            else:
                return {'error': error_message}, status.HTTP_400_BAD_REQUEST
        else:
            return {"error": error}, 400


class LoginUser(Resource):
    """
    Defines methods for manipulating a single user
    """
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
                return make_response(jsonify({'error': 'No data provided'}), status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            response = {"error": str(e)}
            return response, status.HTTP_400_BAD_REQUEST

        user = User.query.filter_by(username=auth['username']).first()

        if not user:
            res = {'error': 'No user with that name exists'}
            return res, status.HTTP_401_UNAUTHORIZED

        if user.verify_password(auth['password']):
            token = jwt.encode(
                {'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
                'topsecret')

            return jsonify({"token": token.decode('UTF-8')})

        return make_response(jsonify({'error': 'Could not verify. Wrong username or password'}), 401,
                             {'WWW-Authentication': 'Basic realm="Login required"'})


class LogoutUser(Resource):
    """
    Defines methods for the Logout Resource
    """
    @token_required
    def post(current_user, self):
        """
                Logout a user
                ---
                tags:
                  - auth
                security:
                    - TokenHeader: []
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


class ResetPassword(Resource):
    """
    Resource to reset a user's password
    """
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
              id: auth
              properties:
                old:
                  default: P@ssword1
                new:
                  default: P@ssw0rd
        responses:
          201:
            description: successfully changed the password
          400:
            description: Bad request. Wrong details, missing parameters and invalid passwords

        """

        password_dict = request.get_json()

        user = User.query.filter_by(id=current_user.id).first()

        if not password_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        try:
            old_password = password_dict['old']
            new_password = password_dict['new']
        except Exception as e:
            response = {"error": str(e)}
            return response, status.HTTP_400_BAD_REQUEST

        if not user.verify_password(old_password):
            response = {'status': 'error', 'message': 'old password is not correct'}
            return response, status.HTTP_400_BAD_REQUEST

        error_message, password_ok = \
            user.check_password_strength_and_hash_if_ok(new_password)
        if password_ok:
            user.update()
            query = User.query.get(user.id)
            result = user_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        else:
            return {'error': error_message}, status.HTTP_400_BAD_REQUEST


api.add_resource(RegisterUser, '/register/')
api.add_resource(LoginUser, '/login/')
api.add_resource(LogoutUser, '/logout/')
api.add_resource(ResetPassword, '/reset-password/')