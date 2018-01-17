import unittest
import json
from flask import url_for
from app import create_app
from api.models import db, User
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

    def test_registration(self):
        """Test user registration works correcty."""
        url = url_for('api/auth.registeruser', _external=True)
        res = self.test_client.post(url, data=json.dumps(self.user_data),
                                    content_type='application/json',
                                    charset='UTF-8')
        self.assertEqual(res.status_code, 201)

    def test_register_with_missing_field(self):
        """Test register when a field is not provided"""
        url = url_for('api/auth.registeruser', _external=True)
        data = {"username": "kev"}
        response = self.test_client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response_data, {"error": "'password'"})
        self.assertEqual(response.status_code, 400)

    def test_register_with_invalid_inputs(self):
        """Test register when an input field is invalid"""
        url = url_for('api/auth.registeruser', _external=True)
        data_2 = {"username": "kev", "password": "k"}
        response_2 = self.test_client.post(
            url,
            data=json.dumps(data_2),
            content_type='application/json'
        )
        response_2_data = json.loads(response_2.get_data(as_text=True))
        self.assertEqual(response_2_data, {"error": "The password is too short"})
        self.assertEqual(response_2.status_code, 400)

    def test_register_when_password_has_no_number(self):
        """Test if register fails when password has no num"""
        url = url_for('api/auth.registeruser', _external=True)
        data_3 = {"username": "kev", "password": "P@ssword"}
        response_3 = self.test_client.post(
            url,
            data=json.dumps(data_3),
            content_type='application/json'
        )
        response_3_data = json.loads(response_3.get_data(as_text=True))
        self.assertEqual(response_3_data, {'error': 'The password must include at least one number'})
        self.assertEqual(response_3.status_code, 400)

    def test_register_with_long_password(self):
        """Test if register fails when a long password is given"""
        url = url_for('api/auth.registeruser', _external=True)
        data_4 = {"username": "kev", "password": "P@ssword1ThereisnothingsimpleaboutcreatingeffectiveJavaScript code"}
        response_4 = self.test_client.post(
            url,
            data=json.dumps(data_4),
            content_type='application/json'
        )
        response_4_data = json.loads(response_4.get_data(as_text=True))
        self.assertEqual(response_4_data, {'error': 'The password is too long'})
        self.assertEqual(response_4.status_code, 400)

    def test_register_when_no_uppercase_letter_pwd(self):
        """Password must contain an uppercase letter"""
        url = url_for('api/auth.registeruser', _external=True)
        data_5 = {"username": "kev", "password": "p@ssword1"}
        response_5 = self.test_client.post(
            url,
            data=json.dumps(data_5),
            content_type='application/json'
        )
        response_5_data = json.loads(response_5.get_data(as_text=True))
        self.assertEqual(response_5_data, {'error': 'The password must include at least one uppercase letter'})

    def test_register_with_no_symbol_in_password(self):
        """Password must have at least on symbol"""
        url = url_for('api/auth.registeruser', _external=True)
        data_6 = {"username": "kev", "password": "Password1"}
        response_6 = self.test_client.post(
            url,
            data=json.dumps(data_6),
            content_type='application/json'
        )
        response_6_data = json.loads(response_6.get_data(as_text=True))
        self.assertEqual(response_6_data, {'error': 'The password must include at least one symbol'})

    def test_register_when_password_has_no_lowercase(self):
        """Password must have at least one lowercase letter"""
        url = url_for('api/auth.registeruser', _external=True)
        data_7 = {"username": "kev", "password": "P@SSWORD1"}
        response_7 = self.test_client.post(
            url,
            data=json.dumps(data_7),
            content_type='application/json'
        )
        response_7_data = json.loads(response_7.get_data(as_text=True))
        self.assertEqual(response_7_data, {'error': 'The password must include at least one lowercase letter'})

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        url = url_for('api/auth.registeruser', _external=True)
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
        self.assertEqual(User.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['username'], new_user_name)

    def test_user_login(self):
        """Test registered user can login."""
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        url = url_for('api/auth.loginuser', _external=True)
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

    def test_login_with_no_data(self):
        """Must contain all fields"""
        url = url_for('api/auth.loginuser', _external=True)
        data = {}
        response = self.test_client.post(
            url,
            data=json.dumps(data),
            content_type='application.json'
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, {'error': 'No data provided'})
        self.assertEqual(response.status_code, 400)

    def test_login_with_wrong_password(self):
        """Should fail when wrong password is provided"""
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        url = url_for('api/auth.loginuser', _external=True)
        data_3 = {"username": "kevin", "password": "Password1"}
        response_2 = self.test_client.post(
            url,
            data=json.dumps(data_3),
            content_type='application/json'
        )
        response_2_data = json.loads(response_2.get_data(as_text=True))
        self.assertEqual(response_2_data, {'error': 'Could not verify. Wrong username or password'})
        self.assertEqual(response_2.status_code, 401)

    def test_login_with_missing_field(self):
        """Should fail when their is missing data"""
        url = url_for('api/auth.loginuser', _external=True)
        data_4 = {"password": "P@ssword1"}
        res_4 = self.test_client.post(
            url,
            data=json.dumps(data_4),
            content_type='application/json'
        )
        res_4_data = json.loads(res_4.get_data(as_text=True))
        self.assertEqual(res_4_data, {"error": "'username'"})
        self.assertEqual(res_4.status_code, 400)

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'username': 'kev',
            'password': 'pass'
        }
        # send a POST request to /auth/login with the data above
        url = url_for('api/auth.loginuser', _external=True)
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
        url = url_for('api/auth.logoutuser', _external=True)
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
        url = url_for('api/auth.logoutuser', _external=True)
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
        url = url_for('api/auth.resetpassword', _external=True)
        response = self.test_client.post(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reset_password_when_old_password_is_wrong(self):
        """Should fail if old password is wrong"""
        url = url_for('api/auth.resetpassword', _external=True)
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code, 201)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        data_2 = {"old": "P@ssw0rd", "new": "P@ssword1"}
        response_2 = self.test_client.post(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data_2),
            content_type='application/json'
        )
        response_2_data = json.loads(response_2.data.decode())
        self.assertEqual(response_2_data, {'status': 'error', 'message': 'old password is not correct'})
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_when_no_data_provided(self):
        """Fail when no data is provided"""
        url = url_for('api/auth.resetpassword', _external=True)
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code, 201)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
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

    def test_reset_when_missing_one_data(self):
        """All data should be provided to pass"""
        url = url_for('api/auth.resetpassword', _external=True)
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code, 201)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
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

    def test_reset_when_password_is_invalid(self):
        """Password must be valid"""
        url = url_for('api/auth.resetpassword', _external=True)
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code, 201)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        data_5 = {"old": "P@ssword1", "new": "P@ssword"}
        response_5 = self.test_client.post(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data_5),
            content_type='application/json'
        )
        response_5_data = json.loads(response_5.data.decode())
        self.assertEqual(response_5_data, {"error": "The password must include at least one number"})
        self.assertEqual(response_5.status_code, status.HTTP_400_BAD_REQUEST)
