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


class User(db.Model, AddUpdateDelete):
    """
    A model to create a user object
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(120), nullable=False)
    created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    recipes = db.relationship('Recipe', backref='user', lazy='dynamic')

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
        self.hashed_password = password_context.encrypt(password)
        return "", True

    def __init__(self, username):
        self.username = username
