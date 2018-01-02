# coding=utf-8
from marshmallow import Schema, fields, pre_load
from marshmallow import validate

from flask_marshmallow import Marshmallow

ma = Marshmallow()


class UserSchema(ma.Schema):
    """
    User model schema
    """
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(3))
    hashed_password = fields.String()
    url = ma.URLFor('api.userresource', id='<id>', _external=True)


class CategorySchema(ma.Schema):
    """
    Schemas sed to validate, serialize and deserialize category models
    """
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(3), missing='')
    url = ma.URLFor('api.categoryresource', id='<id>', _external=True)
    recipes = fields.Nested('RecipeSchema', many=True,
                            exclude=('category',))


class RecipeSchema(ma.Schema):
    """
    Schemas used to validate, serialize and deserialize recipe model
    """
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(1))
    body = fields.String(required=True, validate=validate.Length(3))
    # created_timestamp = fields.Integer(default=datetime.datetime.now())
    # modified_timestamp = fields.Integer(default=datetime.datetime.now())
    user_id = fields.Integer(dump_only=True)
    category = fields.Nested(CategorySchema, only=['id', 'url', 'name'],
                             required=True)
    url = ma.URLFor('api.recipelistresource', id='<id>', _external=True)

    @pre_load
    def process_category(self, data):
        """
        Method to process the serialized data
        """
        category = data.get('category')
        if category:
            if isinstance(category, dict):
                category_name = category.get('name')
            else:
                category_name = category
            category_dict = dict(name=category_name)
        else:
            category_dict = {}
        data['category'] = category_dict
        return data
