# coding=utf-8
import datetime

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
    name = fields.String(required=True, validate=validate.Length(3))
    url = ma.URLFor('api.categoryresource', id='<id>', _external=True)
    recipes = fields.Nested('RecipeSchema', many=True,
                            exclude=('category',))
