import unittest
from app import create_app
from api.models import db
from flask import url_for, json


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """
        Initial set up
        """
        """Set up test variables."""
        self.app = create_app("test_config")
        # initialize the test client
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        self.test_username = 'kevin'
        self.test_user_password = 'P@ssword1'

        self.user_data = {
            "username": "kevin",
            "password": "P@ssword1"
        }

        with self.app_context:
            # create all tables
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_user(self, username, password):
        url = url_for('api/auth.registeruser', _external=True)
        data = {'username': username, 'password': password}
        response = self.test_client.post(
            url,
            content_type='application/json',
            charset='UTF-8',
            data=json.dumps(data)
        )
        return response

    def login_user(self, username, password):
        url = url_for('api/auth.loginuser', _external=True)
        data = {'username': username, 'password': password}
        response = self.test_client.post(
            url,
            content_type='application/json',
            charset='UTF-8',
            data=json.dumps(data))
        return response
