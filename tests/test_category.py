# coding=utf-8
from app import create_app
import json
from flask import url_for
from api.models import db, Category
from api import status
import unittest


class CategoryTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test_config')
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_username = 'kevin'
        self.test_user_password = 'P@ssword1'
        with self.app_context:
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @staticmethod
    def get_accept_content_type_headers():
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_request_without_authentication(self):
        response = self.test_client.get(
            url_for('api.recipelistresource', _external=True),
            headers=self.get_accept_content_type_headers()
        )
        self.assertTrue(response.status_code == status.HTTP_401_UNAUTHORIZED)

    def create_user(self, username, password):
        url = url_for('api/auth.registeruser', _external=True)
        data = {'username': username, 'password': password}
        response = self.test_client.post(
            url,
            headers=self.get_accept_content_type_headers(),
            data=json.dumps(data)
        )
        return response

    def login_user(self, username, password):
        url = url_for('api/auth.loginuser', _external=True)
        data = {'username': username, 'password': password}
        response = self.test_client.post(
            url,
            headers=self.get_accept_content_type_headers(),
            data=json.dumps(data))
        return response

    def create_category(self, name):
        self.create_user(self.test_username, self.test_user_password)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url = url_for('api/categories.categorylistresource', _external=True)
        data = {'name': name}
        response = self.test_client.post(
            url,
            headers={"x-access-token":access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        return response

    def test_create_and_retrieve_category(self):
        self.create_user(self.test_username, self.test_user_password)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        new_category_name = 'soup'
        post_response = self.create_category(new_category_name)
        self.assertEqual(post_response.status_code, 201)
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['name'], new_category_name)
        new_category_url = post_response_data['url']
        get_response = self.test_client.get(
            new_category_url,
            headers={"x-access-token":access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['name'], new_category_name)

    def test_retrieve_category_with_nonexistent_id(self):
        """Test retrieve category by an id not existing"""
        self.create_user(self.test_username, self.test_user_password)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url = '/api/categories/10'
        get_response_2 = self.test_client.get(
            url,
            headers={"x-access-token": access_token}
        )
        get_response_2_data = json.loads(get_response_2.get_data(as_text=True))
        self.assertEqual(get_response_2_data, {"Error": "No category with that Id"})
        self.assertEqual(get_response_2.status_code, 404)

    def test_create_category_with_no_data(self):
        """Fail when no data is provided"""
        self.create_user(self.test_username, self.test_user_password)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url = '/api/categories/'
        data = {}
        post_response_2 = self.test_client.post(
            url,
            data=json.dumps(data),
            headers={"x-access-token": access_token},
            content_type='application/json'
        )
        post_response_2_data = json.loads(post_response_2.get_data(as_text=True))
        self.assertEqual(post_response_2_data, {'message': 'No output data provided'})
        self.assertEqual(post_response_2.status_code, 400)

    def test_create_category_with_invalid_data(self):
        """Category must have min length of 3"""
        self.create_user(self.test_username, self.test_user_password)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url = '/api/categories/'
        data_2 = {"name": "k"}
        post_response_3 = self.test_client.post(
            url,
            data=json.dumps(data_2),
            headers={"x-access-token": access_token},
            content_type='application/json'
        )
        post_response_3_data = json.loads(post_response_3.get_data(as_text=True))
        self.assertEqual(post_response_3_data, {'name': ['Shorter than minimum length 3.']})
        self.assertEqual(post_response_3.status_code, 400)

    def test_create_category_with_invalid_name(self):
        """Category name must be valid"""
        self.create_user(self.test_username, self.test_user_password)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url = '/api/categories/'
        data_3 = {"name": "       "}
        post_response_4 = self.test_client.post(
            url,
            data=json.dumps(data_3),
            headers={"x-access-token": access_token},
            content_type='application/json'
        )
        post_response_4_data = json.loads(post_response_4.get_data(as_text=True))
        self.assertEqual(post_response_4_data, {'error': 'Must contain no spaces and should be a string'})
        self.assertEqual(post_response_4.status_code, 400)

    def test_create_duplicated_category(self):
        """
        Ensure we can not create a duplicated category
        """
        new_category_name = 'soup'
        post_response = self.create_category(new_category_name)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['name'], new_category_name)
        second_post_response = self.create_category(new_category_name)
        self.assertEqual(second_post_response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.query.count(), 1)

    def test_retrieve_categories_list(self):
        """
        Ensure we can retrieve the categories list
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        new_category_name_1 = 'soup'
        post_response_1 = self.create_category(new_category_name_1)
        self.assertEqual(post_response_1.status_code,
                         status.HTTP_201_CREATED)
        new_category_name_2 = 'warning'
        post_response_2 = self.create_category(new_category_name_2)
        self.assertEqual(post_response_2.status_code,
                         status.HTTP_201_CREATED)
        url = url_for('api/categories.categorylistresource', _external=True)
        get_response = self.test_client.get(
            url,
            headers={"x-access-token": access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response_data['results']), 2)
        self.assertEqual(get_response_data['results'][0]['name'],
                         new_category_name_1)
        self.assertEqual(get_response_data['results'][1]['name'],
                         new_category_name_2)

    def test_retrieve_category_page_not_found(self):
        """Fail if page not found"""
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url_2 = '/api/categories/?page=2'
        response = self.test_client.get(
            url_2,
            headers={"x-access-token": access_token}
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, {'Error': 'Category not found'})

    def test_category_with_search(self):
        """Retrieve a searcged category"""
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        new_category_name_1 = 'soup'
        self.create_category(new_category_name_1)
        url_2 = '/api/categories/?q=soup'
        response_2 = self.test_client.get(
            url_2,
            headers={"x-access-token": access_token}
        )
        response_2_data = json.loads(response_2.get_data(as_text=True))
        print(response_2_data)
        self.assertEqual(response_2_data['results'][0]['name'], 'soup')
        self.assertEqual(response_2.status_code, 200)

    def test_not_found_search(self):
        """Searched category not found"""
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url_3 = '/api/categories/?q=meat'
        response_3 = self.test_client.get(
            url_3,
            headers={"x-access-token": access_token}
        )
        response_3_data = json.loads(response_3.get_data(as_text=True))
        self.assertEqual(response_3_data, {"Error": "No categories. Please add a category"})

    def test_update_existing_category(self):
        """
        Ensure we can update the name for an existing category
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        new_category_name_1 = 'soup'
        post_response_1 = self.create_category(new_category_name_1)
        self.assertEqual(post_response_1.status_code,
                         status.HTTP_201_CREATED)
        post_response_data_1 = json.loads(
            post_response_1.get_data(as_text=True))
        new_category_url = post_response_data_1['url']
        new_category_name_2 = 'meat soup'
        data = {"name": new_category_name_2}
        put_response = self.test_client.put(
            new_category_url,
            headers={"x-access-token":access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        get_response = self.test_client.get(
            new_category_url,
            headers={"x-access-token": access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['name'], new_category_name_2)
        new_category_name_3 = 'Beef'
        create_response = self.create_category(
            new_category_name_3
        )
        self.assertEqual(create_response.status_code, 201)
        data = {'name': new_category_name_3}
        put_response_3 = self.test_client.put(
            new_category_url,
            headers={"x-access-token":access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(put_response_3.data.decode())
        self.assertEqual(put_response_3.status_code, 400)
        self.assertEqual(result, {'error': 'A category with the same name already exists'})
        put_response_2 = self.test_client.put(
            new_category_url,
            headers={"x-access-token": access_token},
            content_type='application/json'
        )
        self.assertEqual(put_response_2.status_code, 400)
        url = '/api/categories/10'
        put_response_4 = self.test_client.put(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        put_response_4_data = json.loads(put_response_4.get_data(as_text=True))
        self.assertEqual(put_response_4_data, {"Error": "A category with that Id does not exist"})
        self.assertEqual(put_response_4.status_code, 404)
        data_5 = {}
        put_response_5 = self.test_client.put(
            new_category_url,
            headers={"x-access-token": access_token},
            data=json.dumps(data_5),
            content_type='application/json'
        )
        put_resonse_5_data = json.loads(put_response_5.get_data(as_text=True))
        self.assertEqual(put_resonse_5_data, {"message": "No input data provided"})
        self.assertEqual(put_response_5.status_code, 400)
        data_6 = {"name": "k"}
        put_response_6 = self.test_client.put(
            new_category_url,
            headers={"x-access-token": access_token},
            data=json.dumps(data_6),
            content_type='application/json'
        )
        put_resonse_6_data = json.loads(put_response_6.get_data(as_text=True))
        self.assertEqual(put_resonse_6_data, {'name': ['Shorter than minimum length 3.']})
        self.assertEqual(put_response_6.status_code, 400)

    def test_delete_category(self):
        """
        Test delete a category is successful
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        new_category_name = 'soup'
        post_response = self.create_category(new_category_name)
        self.assertEqual(post_response.status_code,
                         status.HTTP_201_CREATED)
        post_response_data = json.loads(
            post_response.get_data(as_text=True))
        new_category_url = post_response_data['url']
        del_response = self.test_client.delete(
            new_category_url,
            headers={"x-access-token":access_token}
        )
        self.assertEqual(del_response.status_code, status.HTTP_200_OK)
        url = '/api/categories/10'
        response = self.test_client.delete(
            url,
            headers={"x-access-token": access_token}
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, {"error": "No category with that id exists"})
        self.assertEqual(response.status_code, 400)
