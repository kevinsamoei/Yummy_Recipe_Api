import json
from flask import url_for
from .base_tests import BaseTestCase
from api import status


class AuthTestCase(BaseTestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        super(AuthTestCase, self).setUp()
        self.register_url = url_for('api/auth.registeruser', _external=True)
        self.login_url = url_for('api/auth.loginuser', _external=True)
        self.logout_url = url_for('api/auth.logoutuser', _external=True)
        self.reset_url = url_for('api/auth.resetpassword', _external=True)
        self.register = self.client.post(self.register_url, data=json.dumps(self.user_data),
                                         content_type='application/json')
        self.login_response = self.login_user(self.test_username, self.test_user_password)
        self.access_token = json.loads(self.login_response.data.decode())['token']

    def test_registration(self):
        """Test user registration works correcty."""
        self.assertEqual(self.register.status_code, 201)

    def test_register_with_missing_field(self):
        """Test register when a field is not provided"""
        data = {"username": "kev"}
        response = self.test_client.post(
            self.register_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response_data, {'message': {'error': "'password'"}})
        self.assertEqual(response.status_code, 400)

    def test_register_with_invalid_inputs(self):
        """Test register when an input field is invalid"""
        data_2 = {"username": "kev", "password": "k"}
        response_2 = self.test_client.post(
            self.register_url,
            data=json.dumps(data_2),
            content_type='application/json'
        )
        response_2_data = json.loads(response_2.get_data(as_text=True))
        self.assertEqual(response_2_data, {'message': {'error': 'The password is too short'}})
        self.assertEqual(response_2.status_code, 400)

    def test_register_when_password_has_no_number(self):
        """Test if register fails when password has no num"""
        data_3 = {"username": "kev", "password": "P@ssword"}
        response_3 = self.test_client.post(
            self.register_url,
            data=json.dumps(data_3),
            content_type='application/json'
        )
        response_3_data = json.loads(response_3.get_data(as_text=True))
        self.assertEqual(response_3_data, {'message': {'error': 'The password must include at least one number'}})
        self.assertEqual(response_3.status_code, 400)

    def test_register_with_long_password(self):
        """Test if register fails when a long password is given"""
        data_4 = {"username": "kev", "password": "P@ssword1ThereisnothingsimpleaboutcreatingeffectiveJavaScript code"}
        response_4 = self.test_client.post(
            self.register_url,
            data=json.dumps(data_4),
            content_type='application/json'
        )
        response_4_data = json.loads(response_4.get_data(as_text=True))
        self.assertEqual(response_4_data, {'message': {'error': 'The password is too long'}})
        self.assertEqual(response_4.status_code, 400)

    def test_register_when_no_uppercase_letter_pwd(self):
        """Password must contain an uppercase letter"""
        data_5 = {"username": "kev", "password": "p@ssword1"}
        response_5 = self.test_client.post(
            self.register_url,
            data=json.dumps(data_5),
            content_type='application/json'
        )
        response_5_data = json.loads(response_5.get_data(as_text=True))
        self.assertEqual(response_5_data, {'message':
                                               {'error': 'The password must include at least one uppercase letter'}})

    def test_register_with_no_symbol_in_password(self):
        """Password must have at least on symbol"""
        data_6 = {"username": "kev", "password": "Password1"}
        response_6 = self.test_client.post(
            self.register_url,
            data=json.dumps(data_6),
            content_type='application/json'
        )
        response_6_data = json.loads(response_6.get_data(as_text=True))
        self.assertEqual(response_6_data, {'message':
                                               {'error': 'The password must include at least one symbol'}})

    def test_register_when_password_has_no_lowercase(self):
        """Password must have at least one lowercase letter"""
        data_7 = {"username": "kev", "password": "P@SSWORD1"}
        response_7 = self.test_client.post(
            self.register_url,
            data=json.dumps(data_7),
            content_type='application/json'
        )
        response_7_data = json.loads(response_7.get_data(as_text=True))
        self.assertEqual(response_7_data, {'message':
                                               {'error': 'The password must include at least one lowercase letter'}})

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        self.test_client.post(self.register_url, data=json.dumps(self.user_data),
                              content_type='application/json')
        second_res = self.test_client.post(self.register_url, data=json.dumps(self.user_data))
        self.assertEqual(second_res.status_code, 400)

    def test_user_login(self):
        """Test registered user can login."""
        login_res = self.test_client.post(self.login_url, data=json.dumps(self.user_data),
                                          content_type='application/json')
        result = json.loads(login_res.data.decode())
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['token'])

    def test_login_with_no_data(self):
        """Must contain all fields"""
        data = {}
        response = self.test_client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application.json'
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, {'message': 'No data provided'})
        self.assertEqual(response.status_code, 400)

    def test_login_with_wrong_password(self):
        """Should fail when wrong password is provided"""
        data = {"username": "kevin", "password": "Password1"}
        response = self.test_client.post(
            self.register_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, {'message': {'error': 'A user with the same name already exists'}})
        self.assertEqual(response.status_code, 409)

    def test_login_with_missing_field(self):
        """Should fail when their is missing data"""
        data = {"password": "P@ssword1"}
        response = self.test_client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, {'message': {'error': "'username'"}})
        self.assertEqual(response.status_code, 400)

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        not_a_user = {
            'username': 'kev',
            'password': 'pass'
        }
        response = self.test_client.post(self.login_url,
                                    data=json.dumps(not_a_user),
                                    content_type='application/json'
                                    )
        self.assertEqual(response.status_code, 401)

    def test_invalid_token(self):
        """Test for invalid token"""
        response = self.client.post(self.logout_url,
                                    headers={"x-access-token": "SDFGHGHDFGHJDFGHXCVBFGHDFGHDFGHDFG"})
        self.assertEqual(response.status_code, 401)

    def test_logout_user(self):
        """Test a user is successfully loggged out
        """
        response = self.test_client.post(
            self.logout_url,
            headers={"x-access-token": self.access_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_out_user_logout(self):
        """Check if logged out user can log in"""
        self.test_client.post(
            self.logout_url,
            headers={"x-access-token": self.access_token}
        )
        logout_response = self.test_client.post(
            self.logout_url,
            headers={"x-access-token": self.access_token}
        )
        response = json.loads(logout_response.data.decode())
        self.assertEqual(logout_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response, {'message': 'Logged out. log in again'})

    def test_reset_password(self):
        """Test if user can reset password successfully"""
        data = {"old": "P@ssword1", "new": "P@ssw0rd"}
        response = self.test_client.post(
            self.reset_url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reset_password_when_old_password_is_wrong(self):
        """Should fail if old password is wrong"""
        data = {"old": "P@ssw0rd", "new": "P@ssword1"}
        response = self.test_client.post(
            self.reset_url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        response__data = json.loads(response.data.decode())
        self.assertEqual(response__data, {'status': 'error', 'message': 'old password is not correct'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_when_no_data_provided(self):
        """Fail when no data is provided"""
        data = {}
        response = self.test_client.post(
            self.reset_url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.data.decode())
        self.assertTrue(response_data, {'message': 'No input data provided'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_when_missing_one_data(self):
        """All data should be provided to pass"""
        data = {"old": "P@ssw0rd"}
        response = self.test_client.post(
            self.reset_url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.data.decode())
        self.assertEqual(response_data, {"error": "'new'"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_when_password_is_invalid(self):
        """Password must be valid"""
        data = {"old": "P@ssword1", "new": "P@ssword"}
        response = self.test_client.post(
            self.register_url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = json.loads(response.data.decode())
        self.assertEqual(response_data, {'message': {'username': ['Missing data for required field.']}})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
