import unittest
import json
from flask import url_for
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
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['username'], new_user_name)

    def test_user_login(self):
        """Test registered user can login."""
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        url = url_for('api.loginuser', _external=True)
        res = self.test_client.post(url,
                                    data=json.dumps(self.user_data),
                                    content_type='application/json')
        self.assertEqual(res.status_code, 200)
        login_res = self.test_client.post(url, data=json.dumps(self.user_data),
                                          content_type='application/json')

        # get the results in json format
        result = json.loads(login_res.data.decode())
        # Assert that the status code is equal to 200
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'username': 'kev',
            'password': 'pass'
        }
        # send a POST request to /auth/login with the data above
        url = url_for('api.loginuser', _external=True)
        res = self.test_client.post(url,
                                    data=json.dumps(not_a_user),
                                    content_type='application/json'
                                    )
        self.assertEqual(res.status_code, 401)

    def test_logout_user(self):
        """Test a user is successfully loggged out
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code, 201)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url = url_for('api.logoutuser', _external=True)
        response = self.test_client.post(
            url,
            headers={"x-access-token": access_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_out_user_logout(self):
        """Check if logged out user can log in"""
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code, 201)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url = url_for('api.logoutuser', _external=True)
        response = self.test_client.post(
            url,
            headers={"x-access-token": access_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        logout2_response = self.test_client.post(
            url,
            headers={"x-access-token": access_token}
        )
        res = json.loads(logout2_response.data.decode())
        self.assertEqual(logout2_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(logout2_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res, {'message': 'Logged out. log in again'})

    def test_reset_password(self):
        """Test if user can reset password successfully"""
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code, 201)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        data = {"old": "P@ssword1", "new": "P@ssw0rd"}
        url = url_for('api.resetpassword', _external=True)
        response = self.test_client.post(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data_2 = {"old": "P@ssword1", "new": "P@ssw0rd"}
        response_2 = self.test_client.post(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data_2),
            content_type='application/json'
        )
        response_2_data = json.loads(response_2.data.decode())
        self.assertEqual(response_2_data, {'status': 'error', 'message': 'old password is not correct'})
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        data_3 = {}
        response_3 = self.test_client.post(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data_3),
            content_type='application/json'
        )
        response_3_data = json.loads(response_3.data.decode())
        self.assertTrue(response_3_data, {'message': 'No input data provided'})
        self.assertEqual(response_3.status_code, status.HTTP_400_BAD_REQUEST)
        data_4 = {"old":"P@ssw0rd"}
        response_4 = self.test_client.post(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data_4),
            content_type='application/json'
        )
        response_4_data = json.loads(response_4.data.decode())
        self.assertEqual(response_4_data, {"error": "'new'"})
        self.assertEqual(response_4.status_code, status.HTTP_400_BAD_REQUEST)
        data_5 = {"old": "P@ssw0rd", "new": "P@ssword"}
        response_5 = self.test_client.post(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data_5),
            content_type='application/json'
        )
        response_5_data = json.loads(response_5.data.decode())
        self.assertEqual(response_5_data, {"error": "The password must include at least one number"})
        self.assertEqual(response_5.status_code, status.HTTP_400_BAD_REQUEST)
