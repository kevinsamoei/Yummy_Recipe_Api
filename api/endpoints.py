# coding=utf-8
import jwt
import datetime

from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource

from models import db, User, DisableTokens
from serializers import UserSchema
from sqlalchemy.exc import SQLAlchemyError

from api import status
from .auth import token_required

api_bp = Blueprint('api', __name__)
user_schema = UserSchema()
api = Api(api_bp)


class UserResource(Resource):
    """
    Class to create the user resource endpoints
    """
    @token_required
    def get(current_user, self, id):
        """
        Get a user with the specified Id
        Retrieves a paginated result set of users.
        ---
        tags:
          - auth
        parameters:
          - in: path
            name: id
            required: true
            description: The ID of a single user
            type: string
        security:
           - TokenParam: []
           - TokenHeader: []
        responses:
          200:
            description: A list of users
            schema:
              id: User
              properties:
                user:
                  type: string
                  default: kevin

                """
        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        user = User.query.get_or_404(id)
        result = user_schema.dump(user).data
        return result


class UserListResource(Resource):
    """
    Class to create endpoint for a collection of users
    """
    @token_required
    def get(current_user, self):
        """
        Get a list of all users
        """
        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        pagination_helper = PaginationHelper(
            request,
            query=User.query,
            resource_for_url='api.userlistresource',
            key_name='results',
            schema=user_schema
        )
        result = pagination_helper.paginate_query()
        return result


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
        username = request_dict['username']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is not None:
            response = {'user': 'A user with the same name already exists'}
            return response, status.HTTP_400_BAD_REQUEST
        try:
            user = User(username=username)
            error_message, password_ok = \
            user.check_password_strength_and_hash_if_ok(request_dict['password'])
            if password_ok:
                user.add(user)
                query = User.query.get(user.id)
                result = user_schema.dump(query).data
                return result, status.HTTP_201_CREATED
            else:
                return {'error': error_message}, status.HTTP_400_BAD_REQUEST
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = {'error': str(e)}
            return resp, status.HTTP_400_BAD_REQUEST


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
        security:
          - basicAuth: []
        responses:
          200:
            description: A token for the user

                """
        # auth = request.get_json()
        # try:
        #     if not auth or not auth['username'] or not auth['password']:
        #         return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})
        # except KeyError as e:
        #     response = jsonify({"error": str(e)})
        #     return response
        #
        # user = User.query.filter_by(username=auth['username']).first()
        #
        # if not user:
        #     return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})
        #
        # if user.verify_password(auth['password']):
        #     token = jwt.encode(
        #         {'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
        #         'topsecret')
        #
        #     return jsonify({"token": token.decode('UTF-8')})
        #
        # return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})

        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})

        user = User.query.filter_by(username=auth.username).first()

        if not user:
            return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})

        if user.verify_password(auth.password):
            token = jwt.encode(
                {'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
                'topsecret')

            return jsonify({"token": token.decode('UTF-8')})

        return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})


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
                    - TokenParam: []
                    - TokenHeader: []
                responses:
                  200:
                    description: A user has been successfully logged out

                        """
        if not current_user.id:
            return jsonify({"Message": "Can not perform that operation. Please log in!"})
        # Get the auth token
        token = request.headers['x-access-token']
        if token:
            res = DisableTokens.query.filter_by(token=token).first()
            if res:
                return jsonify({"Message": "Token already blacklisted. Please login again"})
            disable_token = DisableTokens(token=token)
            try:
                db.session.add(disable_token)
                db.session.commit()
                return make_response(jsonify({"Message": "Successfully logged out"}), 200)
            except Exception as e:
                return make_response(jsonify({"Message": "Fail!", "Error": e}), 200)
        else:
            return jsonify({"Status": "Fail", "message": "Provide a valid auth token"})


class ResetPassword(Resource):
    """
    Resource to reset a user's password
    """
    def post(self):
        """
        Reset password
        """
        pass

api.add_resource(UserListResource, '/auth/users/')
api.add_resource(UserResource, '/auth/users/<int:id>')
api.add_resource(RegisterUser, '/auth/register/')
api.add_resource(LoginUser, '/auth/login/')
api.add_resource(LogoutUser, '/auth/logout/')
