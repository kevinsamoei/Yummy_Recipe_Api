# coding=utf-8
import datetime
import re

from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as password_context

db = SQLAlchemy()


class AddUpdateDelete():
    """ Object to define methods for add, update and delete resources
    """
    def add(self, resource):
        """
        Create a new resource
        """
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        """
        Update a particular resource
        """
        return db.session.commit()

    def delete(self, resource):
        """
        Delete a resource
        """
        db.session.delete(resource)
        return db.session.commit()

    @staticmethod
    def validate_data(ctx):
        """
        :param ctx:
        :return: True if pattern is matched otherwise return false
        """
        if re.search(r'[a-zA-Z0-9]', ctx) is None:
            return "No input data provided", False
        if '  ' in ctx:
            return "The parameter has more than one spaces in: {}".format(ctx), False
        return "", True


class User(db.Model, AddUpdateDelete):
    """
    A model to create a user object
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(120), nullable=False)
    created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    recipes = db.relationship('Recipe', backref='user', lazy='dynamic',
                              cascade="all, delete-orphan")

    def verify_password(self, password):
        """
        Check if password provided is the hashed password in the db
        """
        return password_context.verify(password, self.hashed_password)

    def check_password_strength_and_hash_if_ok(self, password):
        """
        Validate password strength
        """
        if len(password) < 8:
            return "The password is too short", False
        if len(password) > 32:
            return "The password is too long", False
        if re.search(r'[A-Z]', password) is None:
            return "The password must include at least one uppercase letter", False
        if re.search(r'[a-z]', password) is None:
            return 'The password must include at least one lowercase letter', False
        if re.search(r'\d', password) is None:
            return "The password must include at least one number", False
        if re.search(r"[@!#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None:
            return "The password must include at least one symbol", False
        if ' ' in password:
            return "The parameter password has spaces in: {}".format(password), False
        self.hashed_password = password_context.encrypt(password)
        return "", True

    @classmethod
    def is_unique(cls, username):
        """
        Ensure the recipe to be created will be unique
        """
        existing_user = cls.query.filter_by(username=username).first()
        if existing_user is None:
            return True
        else:
            if existing_user.id == id:
                return True
            else:
                return False

    def __init__(self, username, email):
        self.username = username
        self.email = email


class Category(db.Model, AddUpdateDelete):
    """
    Model to define the category object
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    @classmethod
    def is_unique(cls, id, name, user_id):
        """
        Ensure that a category to be created is unique
        """
        existing_category = cls.query.filter_by(name=name, user_id=user_id).first()
        if existing_category is None:
            return True
        else:
            if existing_category.id == id:
                return True
            else:
                return False


class Recipe(db.Model, AddUpdateDelete):
    """
    Model to define the recipe object
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(500))
    created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    modified_timestamp = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'))
    category = db.relationship('Category', backref=db.backref('recipes',
                                                              lazy='dynamic', order_by='Recipe.title',
                                                              cascade="all, delete-orphan"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, category_id, user):
        self.title = title
        self.body = body
        self.category_id = category_id
        self.user = user

    @classmethod
    def is_unique(cls, id, title, user_id):
        """
        Ensure the recipe to be created will be unique
        """
        existing_recipe = cls.query.filter_by(title=title, user_id=user_id).first()
        if existing_recipe is None:
            return True
        else:
            if existing_recipe.id == id:
                return True
            else:
                return False

    @classmethod
    def validate_recipe(cls, ctx):
        """
        :param ctx:
        :return: True if pattern is matched otherwise return false
        """
        if re.search(r'[a-zA-Z0-9]', ctx) is None:
            return "No input data provided", False
        if '  ' in ctx:
            return "The parameter category has more than one spaces in: {}".format(ctx), False
        return "", True


class DisableTokens(db.Model):
    """
    Class to create a table to store logged out tokens
    """
    __tablename__ = 'disable_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(token):
        res = DisableTokens.query.filter_by(token=token).first()
        if res:
            return True
        else:
            return False
