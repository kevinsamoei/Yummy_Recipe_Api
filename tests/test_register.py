import unittest
import json
from flask import url_for, current_app
from app import create_app
from models import db, User
from api import status

class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app("test_config")
        # initialize the test client
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        # This is the user test json data with a predefined email and password
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
        url = url_for('api.registeruser', _external=True)
        data = {'username': username, 'password': password}
        response = self.test_client.post(
            url,
            content_type='application/json',
            charset='UTF-8',
            data=json.dumps(data)
        )
        return response

    def login_user(self, username, password):
        url = url_for('api.loginuser', _external=True)
        data = {'username': username, 'password': password}
        response = self.test_client.post(
            url,
            content_type='application/json',
            charset='UTF-8',
            data=json.dumps(data))
        return response


    def test_registration(self):
        """Test user registration works correcty."""
        url = url_for('api.registeruser', _external=True)
        res = self.test_client.post(url, data=json.dumps(self.user_data),
                                 content_type='application/json',
                                 charset='UTF-8')
        self.assertEqual(res.status_code, 201)

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        url = url_for('api.registeruser', _external=True)
        res = self.test_client.post(url, data=json.dumps(self.user_data),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 201)
        second_res = self.test_client.post(url, data=json.dumps(self.user_data))
        self.assertEqual(second_res.status_code, 400)

    def test_create_and_retrieve_user(self):
        """
        Ensure we can create a new User and then retrieve it
        """
        new_user_name = self.test_username
        new_user_password = self.test_user_password
        post_response = self.create_user(new_user_name, new_user_password)
        self.assertEqual(post_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        self.assertEqual(User.query.count(), 1)
        post_response_data =json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['username'], new_user_name)
        new_user_url = post_response_data['url']
        get_response = self.test_client.get(
            new_user_url,
            headers={"x-access-token":access_token})
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['username'], new_user_name)

    # def test_user_login(self):
    #     """Test registered user can login."""
    #     create_user_response = self.create_user(self.test_username,
    #                                             self.test_user_password)
    #     self.assertEqual(create_user_response.status_code,
    #                      status.HTTP_201_CREATED)
    #     url = url_for('api.loginuser', _external=True)
    #     res = self.test_client.post(url,
    #                                 data=json.dumps(self.user_data))
    #     self.assertEqual(res.status_code, 201)
    #     login_res = self.test_client.post(url, data=self.user_data)
    #
    #     # get the results in json format
    #     result = json.loads(login_res.data.decode())
    #     # Assert that the status code is equal to 200
    #     self.assertEqual(login_res.status_code, 200)
    #     self.assertTrue(result['token'])
    #
    # def test_non_registered_user_login(self):
    #     """Test non registered users cannot login."""
    #     # define a dictionary to represent an unregistered user
    #     not_a_user = {
    #         'email': 'not@example.com',
    #         'password': 'nope'
    #     }
    #     # send a POST request to /auth/login with the data above
    #     url = url_for('api.loginuser', _external=True)
    #     res = self.test_client.post(url, data=json.dumps(not_a_user),
    #                                 content_type='application/json')
    #     # get the result in json
    #     result = json.loads(res.data.decode())
    #
    #     # assert that this response must contain an error message
    #     # and an error status code 401(Unauthorized)
    #     self.assertEqual(res.status_code, 401)
