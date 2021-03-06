from flask import Blueprint, request, jsonify, make_response, abort
from flask_restful import Api, Resource

from api.models import Category
from api.serializers import CategorySchema

from api import status
from api.pagination import Pagination
from api.auth import token_required
from api.validate_json import validate_json

api_bp = Blueprint('api/categories', __name__)
category_schema = CategorySchema()
api = Api(api_bp)


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
        category = Category.query.filter_by(id=id, user_id=current_user.id).first()
        if not category:
            response = {"Error": "Category with id {0} not found".format(id)}
            return response, status.HTTP_404_NOT_FOUND
        result = category_schema.dump(category).data
        return result

    @validate_json
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

        category = Category.query.filter_by(id=id, user_id=current_user.id).first()
        if not category:
            return {"Error": "A category with that Id does not exist"}, 404
        category_dict = request.get_json(force=True)
        if 'name' in category_dict:
            category_name = category_dict['name'].strip()
            errors = category_schema.validate(category_dict)
            if errors:
                abort(status.HTTP_400_BAD_REQUEST, errors)
            error, validated_name = Category.validate_data(ctx=category_name)
            if validated_name:
                if Category.is_unique(id=id, name=category_name, user_id=current_user.id):
                    category.name = category_name
                else:
                    abort(status.HTTP_409_CONFLICT, 'A category with the same name already exists')
            else:
                return {"errors": error}
        category.update()
        return {'message': 'Category successfully edited!'}, 201

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

        category = Category.query.filter_by(id=id, user_id=current_user.id).first()
        if not category:
            return {"error": "No category with that id {0} exists".format(id)}, 404

        category.delete(category)
        response = make_response(jsonify({"message": "Successfully deleted"}), status.HTTP_200_OK)
        return response


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
        parameters:
          - in: query
            name: q
            description: Search parameter
          - in: query
            name: limit
            description: Number of categories to display per page
          - in: query
            name: page
            description: Page to view
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
        per_page = request.args.get('limit', default=6, type=int)
        page = request.args.get('page', default=1, type=int)

        pagination_helper = Pagination(
            request,
            query=Category.query.filter_by(user_id=current_user.id).order_by("id desc"),
            resource_for_url='api/categories.categorylistresource',
            key_name='results',
            page=page,
            results_per_page=per_page,
            schema=category_schema
        )
        search = request.args.get('q')

        if search:
            categories = Pagination(
                request,
                query=Category.query.filter(
                    Category.user_id == current_user.id,
                    Category.name.ilike("%" + search + "%")),
                resource_for_url='api/categories.categorylistresource',
                key_name='results',
                page=page,
                results_per_page=per_page,
                schema=category_schema
            )
            results = categories.paginate_query()
            if len(results['results']) <= 0:
                return jsonify({"error": "No category match found for search term"})
            return results, 200

        result = pagination_helper.paginate_query()
        if len(result['results']) <= 0:
            res = {"error": "No categories found"}
            return res, 400
        return result, status.HTTP_200_OK

    @validate_json
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
        request_dict = request.get_json()
        if not request_dict:
            return {'message': 'No output data provided'}, 400
        errors = category_schema.validate(request_dict)
        if errors:
            return {'message': errors}, 400

        category_name = request_dict['name'].strip()
        if not Category.is_unique(id=0, name=category_name, user_id=current_user.id):
            return {'message': 'A category with the same name already exists'}, 400
        error, validated_name = Category.validate_data(ctx=category_name)
        if validated_name:
            category = Category(category_name, user_id=current_user.id)
            category.add(category)
            result = {'message': 'Category successfully added!'}
            return result, status.HTTP_201_CREATED
        else:
            return {'message': error}, 400


api.add_resource(CategoryListResource, '/')
api.add_resource(CategoryResource, '/<int:id>')