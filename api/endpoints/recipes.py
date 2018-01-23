# coding=utf-8
from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource

from api.models import db, Category,Recipe
from api.serializers import RecipeSchema

from api import status
from api.pagination import Pagination
from api.auth import token_required

api_bp = Blueprint('api', __name__)
recipe_schema = RecipeSchema()
api = Api(api_bp)


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

        try:
            recipe = Recipe.query.get_or_404(id)
            result = recipe_schema.dump(recipe).data
            return result
        except Exception:
            response = {"Error": "A recipe with that Id does not exist"}
            return response, status.HTTP_404_NOT_FOUND

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

        recipe = Recipe.query.filter_by(id=id).first()
        if not recipe:
            return {"Error": "A recipe with that Id does not exist"}, 400
        recipe_dict = request.get_json(force=True)
        if 'title' in recipe_dict:
            recipe_title = recipe_dict['title'].lower()
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

        recipe.update()
        return self.get(id)

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

        recipe = Recipe.query.filter_by(id=id).first()
        if not recipe:
            res = {"error": "A recipe with the the id of {0} does not exist".format(id)}
            return res, status.HTTP_400_BAD_REQUEST

        recipe.delete(recipe)
        response = make_response(jsonify({"Message": "Deleted"}), status.HTTP_200_OK)
        return response


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
          - in: query
            name: q
            description: Search parameter q
          - in: query
            name: limit
            description: The limit of recipes
          - in: query
            name: page
            description: The page to display
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

        per_page = request.args.get('limit', default=5, type=int)
        page = request.args.get('page', default=1, type=int)

        pagination_helper = Pagination(
            request,
            query=Recipe.query.filter(Recipe.user_id == current_user.id),
            resource_for_url='api.recipelistresource',
            results_per_page=per_page,
            page=page,
            key_name='results',
            schema=recipe_schema
        )
        search = request.args.get('q')

        if search:
            recipes = Pagination(
                request,
                query=Recipe.query.filter(
                    Recipe.user_id == current_user.id,
                    (Recipe.title.contains(search)) |
                    (Recipe.body.contains(search))),
                resource_for_url='api.recipelistresource',
                key_name='results',
                page=page,
                results_per_page=per_page,
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

        request_dict = request.get_json()

        if not request_dict:
            response = {"Message": "No output data provided"}
            return response, status.HTTP_400_BAD_REQUEST
        errors = recipe_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        recipe_title = request_dict['title'].lower()
        recipe_body = request_dict['body']
        if not Recipe.is_unique(id=0, title=recipe_title):
            response = {'error': 'A recipe with the same title already exists'}
            return response, status.HTTP_400_BAD_REQUEST
        error, validated_title = Recipe.validate_recipe(ctx=recipe_title)
        if not validated_title:
            return {"error": error}, 400
        error_body, validated_body = Recipe.validate_recipe(ctx=recipe_body)
        if not validated_body:
            return {"error": error_body}, 400
        category_name = request_dict['category']['name'].lower()
        error_category, validate_data = Category.validate_data(ctx=category_name)
        if validate_data:
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
        else:
            return {"error": error_category}, 400


api.add_resource(RecipeListResource, '/recipes/')
api.add_resource(RecipeResource, '/recipes/<int:id>')
