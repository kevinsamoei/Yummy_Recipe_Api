# coding=utf-8
import json
from flask import url_for
from api.models import Category
from api import status
from .base_tests import BaseTestCase


class CategoryTests(BaseTestCase):
    def setUp(self):
        super(CategoryTests, self).setUp()
        self.category_url = url_for('api/categories.categorylistresource', _external=True)
        self.category_name = "soup"
        self.register = self.client.post("api/auth/register/", data=json.dumps(self.user_data),
                                         content_type='application/json')
        self.login_response = self.login_user(self.test_username, self.test_user_password)
        self.access_token = json.loads(self.login_response.data.decode())['token']
        self.category = self.create_category(self.category_name)

    @staticmethod
    def get_accept_content_type_headers():
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_request_without_authentication(self):
        response = self.test_client.get(
            self.category_url
        )
        self.assertTrue(response.status_code == status.HTTP_401_UNAUTHORIZED)

    def create_category(self, name):
        data = {'name': name}
        response = self.test_client.post(
            self.category_url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        return response

    def test_create_category(self):
        self.assertEqual(self.category.status_code, 201)
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(self.category.get_data(as_text=True))
        self.assertEqual(post_response_data['name'], self.category_name)

    def test_retrieve_category(self):
        url = '/api/categories/1'
        get_response = self.test_client.get(
            url,
            headers={"x-access-token": self.access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['name'], self.category_name)

    def test_retrieve_category_with_nonexistent_id(self):
        """Test retrieve category by an id not existing"""
        get_response = self.test_client.get(
            '/api/categories/10',
            headers={"x-access-token": self.access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response_data, {'Error': 'Category with id 10 not found'})
        self.assertEqual(get_response.status_code, 404)

    def test_create_category_with_no_data(self):
        """Fail when no data is provided"""
        data = {}
        post_response = self.test_client.post(
            self.category_url,
            data=json.dumps(data),
            headers={"x-access-token": self.access_token},
            content_type='application/json'
        )
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data, {'message': 'No output data provided'})
        self.assertEqual(post_response.status_code, 400)

    def test_create_category_with_invalid_data(self):
        """Category must have min length of 3"""
        data = {"name": "k"}
        post_response = self.test_client.post(
            self.category_url,
            data=json.dumps(data),
            headers={"x-access-token": self.access_token},
            content_type='application/json'
        )
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['message'], {'name': ['Shorter than minimum length 3.']})
        self.assertEqual(post_response.status_code, 400)

    def test_create_category_with_invalid_name(self):
        """Category name must be valid"""

        data = {"name": "       "}
        post_response = self.test_client.post(
            self.category_url,
            data=json.dumps(data),
            headers={"x-access-token": self.access_token},
            content_type='application/json'
        )
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data, {'message': 'No input data provided'})
        self.assertEqual(post_response.status_code, 400)

    def test_create_duplicated_category(self):
        """
        Ensure we can not create a duplicated category
        """
        new_category_name = 'soup'
        response = self.create_category(new_category_name)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Category.query.count(), 1)

    def test_retrieve_categories_list(self):
        """
        Ensure we can retrieve the categories list
        """
        new_category_name_2 = 'warning'
        self.create_category(new_category_name_2)
        get_response = self.test_client.get(
            '/api/categories/',
            headers={"x-access-token": self.access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(len(get_response_data['results']), 2)
        self.assertEqual(get_response_data['results'][0]['name'],
                         self.category_name)
        self.assertEqual(get_response_data['results'][1]['name'],
                         new_category_name_2)

    def test_retrieve_category_page_not_found(self):
        """Fail if page not found"""
        response = self.test_client.get(
            '/api/categories/?page=2',
            headers={"x-access-token": self.access_token}
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data['Error'], 'No categories found')

    def test_category_with_search(self):
        """Retrieve a searcged category"""
        response = self.test_client.get(
            '/api/categories/?q=s',
            headers={"x-access-token": self.access_token}
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data['results'][0]['name'], 'soup')

    def test_not_found_search(self):
        """Searched category not found"""
        response_3 = self.test_client.get(
            '/api/categories/?q=m',
            headers={"x-access-token": self.access_token}
        )
        response_3_data = json.loads(response_3.get_data(as_text=True))
        self.assertEqual(response_3_data["Error"], "No catgory match found for search term")

    def test_update_existing_category(self):
        """
        Ensure we can update the name for an existing category
        """
        url = 'api/categories/1'
        new_category_name = 'meat soup'
        data = {"name": new_category_name}
        put_response = self.test_client.put(
            url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        get_response = self.test_client.get(
            url,
            headers={"x-access-token": self.access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response_data['name'], new_category_name)

    def test_update_category_with_nonexistent_id(self):
        """A category that does not exist"""
        url = '/api/categories/10'
        data = {"name": self.category_name}
        put_response = self.test_client.put(
            url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        put_response_data = json.loads(put_response.get_data(as_text=True))
        self.assertEqual(put_response_data, {"Error": "A category with that Id does not exist"})
        self.assertEqual(put_response.status_code, 404)

    def test_update_category_with_invalid_data(self):
        """Update with invalid data"""
        data = {"name": "k"}
        put_response = self.test_client.put(
            'api/categories/1',
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        put_response_data = json.loads(put_response.get_data(as_text=True))
        self.assertEqual(put_response_data, {'message': {'name': ['Shorter than minimum length 3.']}})
        self.assertEqual(put_response.status_code, 400)

    def test_delete_category(self):
        """
        Test delete a category is successful
        """
        delete_response = self.test_client.delete(
            'api/categories/1',
            headers={"x-access-token": self.access_token}
        )
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

    def test_delete_non_exitent_category(self):
        """Test delete a category not existing"""
        url = '/api/categories/10'
        response = self.test_client.delete(
            url,
            headers={"x-access-token": self.access_token}
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data['error'], 'No category with that id 10 exists')
        self.assertEqual(response.status_code, 404)
