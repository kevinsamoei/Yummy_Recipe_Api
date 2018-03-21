# coding=utf-8
from flask import Blueprint, request, jsonify, make_response, abort
from flask_restful import Api, Resource

from api.models import db, Category,Recipe
from api.serializers import RecipeSchema

from api import status
from api.pagination import Pagination
from api.auth import token_required
from api.validate_json import validate_json

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
        """

        recipe = Recipe.query.filter_by(id=id, user_id=current_user.id).first()
        result = recipe_schema.dump(recipe).data
        if len(result) <= 0:
            response = {"Error": "A recipe with Id {0} does not exist".format(id)}
            return response, status.HTTP_404_NOT_FOUND
        return result

    @validate_json
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
                      """

        recipe = Recipe.query.filter_by(id=id, user_id=current_user.id).first()
        if not recipe:
            return {"Error": "A recipe with that Id does not exist"}, 404
        recipe_dict = request.get_json(force=True)
        if 'title' in recipe_dict:
            recipe_title = recipe_dict['title'].strip()
            error, validate_title = recipe.validate_recipe(ctx=recipe_title)
            if validate_title:
                if Recipe.is_unique(id=id, title=recipe_title, user_id=current_user.id):
                    recipe.title = recipe_title
                else:
                    abort(status.HTTP_409_CONFLICT, 'A recipe with the same title already exists')
            else:
                abort(400, {"error": error})
        if 'body' in recipe_dict:
            recipe_body = recipe_dict['body'].strip()
            body_errors, validate_body = recipe.validate_recipe(ctx=recipe_body)
            if validate_body:
                recipe.body = recipe_body
            else:
                abort(400, body_errors)

        dumped_recipe, dumped_errors = recipe_schema.dump(recipe)
        if dumped_errors:
            abort(status.HTTP_400_BAD_REQUEST, dumped_errors)

        recipe.update()
        return {"message": "Recipe successfully edited"}, 200

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

        recipe = Recipe.query.filter_by(id=id, user_id=current_user.id).first()
        if not recipe:
            res = {"error": "A recipe with the the id of {0} does not exist".format(id)}
            return res, status.HTTP_404_NOT_FOUND

        recipe.delete(recipe)
        response = make_response(jsonify({"Message": "Recipe deleted"}), status.HTTP_200_OK)
        return response


class RecipeListResource(Resource):
    """
    This class describes the object to retrieve a collection of recipes
    """
    @token_required
    def get(current_user, self, category_id):
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
          - in: path
            name: category_id
            description: Category Id
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
        """

        per_page = request.args.get('limit', default=9, type=int)
        page = request.args.get('page', default=1, type=int)
        category = Category.query.filter_by(id=category_id).first()

        pagination_helper = Pagination(
            request,
            query=Recipe.query.filter_by(category_id=category_id, user_id=current_user.id).order_by("id desc"),
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
                    Recipe.category_id == category_id,
                    (Recipe.title.ilike("%" + search + "%")) |
                    (Recipe.body.contains(search.title()))),
                resource_for_url='api.recipelistresource',
                key_name='results',
                page=page,
                results_per_page=per_page,
                schema=recipe_schema
            )
            results = recipes.paginate_query()
            if len(results['results']) <= 0:
                response = {"error": "No recipe found for that search."}
                return response, 404
            return results, status.HTTP_200_OK
        result = pagination_helper.paginate_query()
        if len(result['results']) <= 0:
            response = {"error": "No recipes."}
            return response, 404
        return result, status.HTTP_200_OK

    @validate_json
    @token_required
    def post(current_user, self, category_id):
        """
        Create a recipe
        ---
        tags:
          - recipes
        parameters:
          - in: path
            name: category_id
            required: true
            description: Category Id
            type: integer
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
        """

        request_dict = request.get_json()

        if not request_dict:
            abort(status.HTTP_400_BAD_REQUEST, "All fields are required")
        errors = recipe_schema.validate(request_dict)
        if errors:
            abort(status.HTTP_400_BAD_REQUEST, errors)
        recipe_title = request_dict['title'].title()
        recipe_body = request_dict['body'].strip()
        if not Recipe.is_unique(id=0, title=recipe_title, user_id=current_user.id):
            abort(status.HTTP_409_CONFLICT, 'A recipe with the same title already exists')
        error, validated_title = Recipe.validate_recipe(ctx=recipe_title)
        if not validated_title:
            abort(400, error)
        error_body, validated_body = Recipe.validate_recipe(ctx=recipe_body)
        if not validated_body:
            abort(400, error_body)
        category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
        if category:
            recipe = Recipe(
                title=recipe_title,
                body=recipe_body,
                category_id=category.id,
                user=current_user
            )
            recipe.add(recipe)
            response = "Recipe uccessfully added!"
            return make_response(jsonify(response), status.HTTP_201_CREATED)
        else:
            abort(400, "A category with Id {0} does not exist".format(category_id))


api.add_resource(RecipeListResource, '/category/<int:category_id>/recipes/')
api.add_resource(RecipeResource, '/recipes/<int:id>')
