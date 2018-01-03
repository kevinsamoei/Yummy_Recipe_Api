# coding=utf-8
import jwt
import datetime

from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource

from models import db, User, Category,Recipe, DisableTokens
from serializers import UserSchema, CategorySchema, RecipeSchema
from sqlalchemy.exc import SQLAlchemyError

from api import status
from .pagination import PaginationHelper
from .auth import token_required

api_bp = Blueprint('api', __name__)
category_schema = CategorySchema()
recipe_schema = RecipeSchema()
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
                return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})
        except KeyError as e:
            response = jsonify({"error": str(e)})
            return response

        user = User.query.filter_by(username=auth['username']).first()

        if not user:
            return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})

        if user.verify_password(auth['password']):
            token = jwt.encode(
                {'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
                'topsecret')

            return jsonify({"token": token.decode('UTF-8')})

        return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})

        # auth = request.authorization
        #
        # if not auth or not auth.username or not auth.password:
        #     return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})
        #
        # user = User.query.filter_by(username=auth.username).first()
        #
        # if not user:
        #     return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})
        #
        # if user.verify_password(auth.password):
        #     token = jwt.encode(
        #         {'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
        #         'topsecret')
        #
        #     return jsonify({"token": token.decode('UTF-8')})
        #
        # return make_response('Could not verify', 401, {'WWW-Authentication': 'Basic realm="Login required"'})


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
    def post(self, id):
        """
        Reset password
        """
        pass


class CategoryResource(Resource):
    """
    Object to define endpoint for the category resource
    """
    @token_required
    def get(current_user, self, id):
        """
        Get a category with the specified id
        ---
        tags:
          - categories
        parameters:
          - in: path
            name: id
            required: true
            description: The ID of the category to retrieve
            type: string
        security:
           - TokenHeader: []
        responses:
          200:
            description: A single category
            schema:
              id: category
              properties:
                name:
                  type: string
                  default: soup
        """
        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        category = Category.query.get_or_404(id)
        if category.user_id == current_user.id:
            result = category_schema.dump(category).data
            return result
        else:
            return jsonify({"error": "Login to access"})

    @token_required
    def put(current_user, self, id):
        """
                      Edit a category with the specified id
                      ---
                      tags:
                        - categories
                      parameters:
                        - in: path
                          name: id
                          required: true
                          description: The ID of the category to retrieve
                          type: string
                        - in: body
                          name: category
                          required: true
                          description: The name of the category
                          type: string
                          schema:
                            id: category
                            properties:
                                name:
                                    type: string
                                    default: soup
                      security:
                         - TokenHeader: []
                      responses:
                        200:
                          description: A single category successfully deleted
                          schema:
                            id: category
                            properties:
                                name:
                                    type: string
                                    default: soup
                      """
        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        category = Category.query.get_or_404(id)
        category_dict = request.get_json()
        if not category_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = category_schema.validate(category_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            if 'name' in category_dict:
                category_name = category_dict['name']
                if Category.is_unique(id=id, name=category_name):
                    category.name = category_name
                else:
                    response = {'error': 'A category with the same name already exists'}
                    return response, status.HTTP_400_BAD_REQUEST
            category.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({'error': str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED

    @token_required
    def delete(current_user, self, id):
        """
                Delete a category with the specified id
                ---
                tags:
                  - categories
                parameters:
                  - in: path
                    name: id
                    required: true
                    description: The ID of the category to retrieve
                    type: string
                security:
                   - TokenHeader: []
                responses:
                  200:
                    description: A single category successfully deleted
                """

        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        category = Category.query.get_or_404(id)
        try:
            category.delete(category)
            response = make_response(jsonify({"message": "successfully deleted"}), status.HTTP_200_OK)
            return response
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED


class CategoryListResource(Resource):
    """
    This class is used to create endpoints for a list of categories
    """
    @token_required
    def get(current_user, self):
        """
        Get a list of categories
        A paginated list of categories
        ---
        tags:
          - categories
        security:
           - TokenHeader: []
        responses:
          200:
            description: A single category
            schema:
              id: Category
              properties:
                name:
                  type: json
                  default: Soup
        """
        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        pagination_helper = PaginationHelper(
            request,
            query=Category.query.filter(
                    Category.user_id == current_user.id),
            resource_for_url='api.categorylistresource',
            key_name='results',
            schema=category_schema
        )
        search = request.args.get('q')

        if search:
            search.strip()
            categories = PaginationHelper(
                request,
                query=Category.query.filter(
                    Category.user_id == current_user.id,
                    Category.name.contains(search)),
                resource_for_url='api.categorylistresource',
                key_name='results',
                schema=category_schema
            )
            results = categories.paginate_query()
            if len(results['results']) <= 0:
                return jsonify({"Error": "No categories. Please add a category"})
            return results

        result = pagination_helper.paginate_query()
        if len(result['results']) <= 0:
            return jsonify({"Error": "No categories. Please add a category"})
        return result
        # categories = Category.query.all()
        # results = category_schema.dump(categories, many=True).data
        # return results

    @token_required
    def post(current_user, self):
        """
        Create a category
        ---
        tags:
          - categories
        parameters:
          - in: body
            name: category
            required: true
            description: The name of the category
            type: string
            schema:
              id: category
              properties:
                name:
                  type: string
                  default: soup
        security:
           - TokenHeader: []
        responses:
          200:
            description: Create a category
            schema:
              id: category
              properties:
                name:
                  type: string
                  default: soup
        """
        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No output data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = category_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST

        category_name = request_dict['name'].title()
        if not Category.is_unique(id=0, name=category_name):
            response = {"error": "A category with the same name already exists"}
            return response, status.HTTP_400_BAD_REQUEST
        validated_name = Category.validate_category(name=category_name)
        if validated_name:
            return {"Error": "Category name is not valid"}
        try:
            category = Category(category_name, user_id=current_user.id)
            category.add(category)
            query = Category.query.get(category.id)
            result = category_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST


class RecipeResource(Resource):
    """
    Resource for the recipe endpoints
    """
    @token_required
    def get(current_user, self, id):
        """
        Get a recipe with the specified id
        ---
        tags:
          - recipes
        parameters:
          - in: path
            name: id
            required: true
            description: The ID of the recipe to retrieve
            type: string
        security:
           - TokenHeader: []
        responses:
          200:
            description: A sing recipe
            schema:
              id: recipe
              properties:
                title:
                  type: string
                  default: Meat soup
                body:
                  type: string
                  default: This is the process of making meat soup
                category:
                  type: string
                  default: Soup
        """

        recipe = Recipe.query.get_or_404(id)
        result = recipe_schema.dump(recipe).data
        return result

    @token_required
    def put(current_user, self, id):
        """
                      Edit and update a recipe with the specified id
                      ---
                      tags:
                        - recipes
                      parameters:
                        - in: path
                          name: id
                          required: true
                          description: The ID of the recipe to edit
                          type: string
                        - in: body
                          name: recipe
                          required: true
                          description: The title and body of the recipe
                          type: string
                          schema:
                            id: recipe
                            properties:
                                title:
                                    type: string
                                    default: Meat soup
                                body:
                                    type: string
                                    default: Pour, mix, cook
                                category:
                                  type: string
                                  default: Soup
                      security:
                         - TokenHeader: []
                      responses:
                        200:
                          description: A single recipe successfully edited
                          schema:
                            id: recipe
                            properties:
                                title:
                                    type: string
                                    default: Meat soup
                                body:
                                    type: string
                                    default: Pour, mix, cook
                                category:
                                  type: string
                                  default: Soup
                      """
        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        recipe = Recipe.query.get_or_404(id)
        recipe_dict = request.get_json(force=True)
        if 'title' in recipe_dict:
            recipe_title = recipe_dict['title']
            if Recipe.is_unique(id=id, title=recipe_title):
                recipe.title = recipe_title
            else:
                response = {'error': 'A recipe with the same title already exists'}
                return response, status.HTTP_400_BAD_REQUEST
        if 'body' in recipe_dict:
            recipe.body = recipe_dict['body']

        dumped_recipe, dumped_errors = recipe_schema.dump(recipe)
        if dumped_errors:
            return dumped_errors, status.HTTP_400_BAD_REQUEST
        try:
            recipe.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST

    @token_required
    def delete(current_user, self, id):
        """
                        Delete a recipe with the specified id
                        ---
                        tags:
                          - recipes
                        parameters:
                          - in: path
                            name: id
                            required: true
                            description: The ID of the recipe to delete
                            type: string
                        security:
                           - TokenHeader: []
                        responses:
                          200:
                            description: A single recipe successfully deleted
                        """

        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        recipe = Recipe.query.get_or_404(id)
        try:
            delete = recipe.delete(recipe)
            response = make_response(jsonify({"Message": "Deleted"}), status.HTTP_200_OK)
            return response
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED


class RecipeListResource(Resource):
    """
    This class describes the object to retrieve a collection of recipes
    """
    @token_required
    def get(current_user, self):
        """
        Get a list of recipes
            A paginated list of recipes
        ---
        tags:
          - recipes
        security:
           - TokenHeader: []
        parameters:
          - in: path
            name: ?q
            description: Search parameter q
        responses:
          200:
            description: A list of recipes
            schema:
              id: Recipes
              properties:
                title:
                  type: json
                  default: Meat Soup
                body:
                  type: json
                  default: Prepare it
                category:
                  type: json
                  default: Soup
        """
        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        pagination_helper = PaginationHelper(
            request,
            query=Recipe.query.filter(Recipe.user_id == current_user.id),
            resource_for_url='api.recipelistresource',
            key_name='results',
            schema=recipe_schema
        )
        search = request.args.get('q')

        if search:
            search.strip()
            recipes = PaginationHelper(
                request,
                query=Recipe.query.filter(
                    Recipe.user_id == current_user.id,
                    (Recipe.title.contains(search)) |
                    (Recipe.body.contains(search))),
                resource_for_url='api.recipelistresource',
                key_name='results',
                schema=recipe_schema
            )
            results = recipes.paginate_query()
            if len(results['results']) <= 0:
                return jsonify({"Error": "No recipes. Create a recipe!"})
            return results
        result = pagination_helper.paginate_query()
        if len(result['results']) <= 0:
            return jsonify({"Error": "No recipes. Create a recipe!"})
        return result

    @token_required
    def post(current_user, self):
        """
        Create a recipe
        ---
        tags:
          - recipes
        parameters:
          - in: body
            name: recipe
            required: true
            description: The title of the recipe
            type: string
            schema:
              id: recipe
              properties:
                title:
                  type: string
                  default: Meat soup
                body:
                  type: string
                  default: This is the process of making meat soup
                category:
                  type: string
                  default: Soup
        security:
           - TokenHeader: []
        responses:
          200:
            description: Create a recipe
            schema:
              id: recipe
              properties:
                title:
                  type: string
                  default: Meat soup
                body:
                  type: string
                  default: This is the process of making meat soup
                category:
                  type: string
                  default: Soup
        """
        if not current_user.id:
            return make_response(jsonify({'message': 'Can not perform that function'}))

        request_dict = request.get_json()

        if not request_dict:
            response = {"Message": "No output data provided"}
            return response, status.HTTP_400_BAD_REQUEST
        errors = recipe_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        recipe_title = request_dict['title'].title()
        recipe_body = request_dict['body']
        if not Recipe.is_unique(id=0, title=recipe_title):
            response = {'error': 'A recipe with the same title already exists'}
            return response, status.HTTP_400_BAD_REQUEST
        validated_title = Recipe.validate_recipe_title(title=recipe_title)
        if validated_title:
            return {"Error": "Recipe title is not valid"}
        validated_body = Recipe.validate_recipe_body(body=recipe_body)
        if validated_body:
            return {"Error": "Recipe body is not valid"}
        try:
            category_name = request_dict['category']['name']
            validate_category = Category.validate_category(name=category_name)
            if validate_category:
                return {"Error": "Not a valid category name"}
            category = Category.query.filter_by(name=category_name).first()
            if category is None:
                category = Category(name=category_name, user_id=current_user.id)
                db.session.add(category)
            recipe = Recipe(
                title=recipe_title,
                body=recipe_body,
                category=category,
                user=current_user
            )
            recipe.add(recipe)
            query = Recipe.query.get(recipe.id)
            result = recipe_schema.dump(query).data

            return make_response(jsonify(result), status.HTTP_201_CREATED)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST


api.add_resource(UserListResource, '/auth/users/')
api.add_resource(UserResource, '/auth/users/<int:id>')
api.add_resource(RegisterUser, '/auth/register/')
api.add_resource(LoginUser, '/auth/login/')
api.add_resource(LogoutUser, '/auth/logout/')
api.add_resource(CategoryListResource, '/categories/')
api.add_resource(CategoryResource, '/categories/<int:id>')
api.add_resource(RecipeListResource, '/recipes/')
api.add_resource(RecipeResource, '/recipes/<int:id>')
