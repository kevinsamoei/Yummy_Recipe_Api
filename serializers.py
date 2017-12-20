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
