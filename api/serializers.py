# coding=utf-8
from marshmallow import fields, pre_load, post_load
from marshmallow import validate

from flask_marshmallow import Marshmallow

ma = Marshmallow()


class UserSchema(ma.Schema):
    """
    User model schema
    """
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(3))
    email = fields.String(required=True, validate=validate.Regexp(r"(^\w+@[a-zA-Z0-9_]+?\.[a-zA-Z0-9]{3,3}$)"
                                                                  , error="Invalid email"))
    hashed_password = fields.String()
    url = ma.URLFor('api/auth.registeruser', id='<id>', _external=True)

    @post_load
    def lowerstrip_email(self, item):
        item['email'] = item['email'].lower().strip()
        return item


class CategorySchema(ma.Schema):
    """
    Schemas sed to validate, serialize and deserialize category models
    """
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(3))
    url = ma.URLFor('api/categories.categoryresource', id='<id>', _external=True)
    created_timestamp = ma.DateTime(format("rfc"), dump_only=True)
    modified_timestamp = ma.DateTime(dump_only=True)
    recipes = fields.Nested('RecipeSchema', many=True,
                            exclude=('category',))


class RecipeSchema(ma.Schema):
    """
    Schemas used to validate, serialize and deserialize recipe model
    """
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(1))
    body = fields.String(required=True, validate=validate.Length(3))
    category_id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    # url = ma.URLFor('api.reciperesource', id='<id>', _external=True)
    category = fields.Nested(CategorySchema, only=['name'],
                             dump_only=True)

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
