# coding=utf-8
from app import create_app
import base64
from base64 import b64encode
from flask import current_app, json, url_for
from models import db, Category, Recipe, User
from api import status
from unittest import TestCase


class InitialTests(TestCase):
    def setUp(self):
        self.app = create_app('test_config')
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_username = 'testuser'
        self.test_user_password = 'P@ssword1'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        # pass

    def get_accept_content_type_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_authentication_headers(self, username, password):

        authentication_headers = self.get_accept_content_type_headers()
        authentication_headers['Authorization'] = \
            'Basic ' + b64encode((username + ':' + password).encode('utf-8')).decode('utf-8')
        return authentication_headers

    def test_request_without_authentication(self):
        response = self.test_client.get(
            url_for('api.recipelistresource', _external=True),
            headers=self.get_accept_content_type_headers()
        )
        self.assertTrue(response.status_code == status.HTTP_401_UNAUTHORIZED)

    def create_user(self, username, password):
        url = url_for('api.registeruser', _external=True)
        data = {'username': username, 'password': password}
        response = self.test_client.post(
            url,
            headers=self.get_accept_content_type_headers(),
            data=json.dumps(data)
        )
        return response

    def create_category(self, name):
        url = url_for('api.categorylistresource', _external=True)
        data = {'name': name}
        response = self.test_client.post(
            url,
            headers=self.get_authentication_headers(self.test_username, self.test_user_password),
            data=json.dumps(data)
        )
        return response

    def test_create_and_retrieve_category(self):
        create_user_response = self.create_user(self.test_username, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name = 'soup'
        post_response = self.create_category(new_category_name)
        self.assertEqual(post_response.status_code,
                         status.HTTP_201_CREATED)
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['name'], new_category_name)
        new_category_url = post_response_data['url']
        get_response = self.test_client.get(
            new_category_url,
            headers=self.get_accept_content_type_headers()
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['name'], new_category_name)

    def test_create_duplicated_category(self):
        """
        Ensure we can not create a duplicated category
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        new_category_name = 'soup'
        post_response = self.create_category(new_category_name)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['name'], new_category_name)
        second_post_response = self.create_category(new_category_name)
        self.assertEqual(second_post_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.query.count(), 1)

    def test_retrieve_categories_list(self):
        """
        Ensure we can retrieve the categories list
        """
        create_user_response = self.create_user(self.test_username, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name_1 = 'Error'
        post_response_1 = self.create_category(new_category_name_1)
        self.assertEqual(post_response_1.status_code, status.HTTP_201_CREATED)
        new_category_name_2 = 'Warning'
        post_response_2 = self.create_category(new_category_name_2)
        self.assertEqual(post_response_2.status_code, status.HTTP_201_CREATED)
        url = url_for('api.categorylistresource', _external=True)
        get_response = self.test_client.get(
            url,
            headers=self.get_authentication_headers(self.test_username, self.test_user_password)
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response_data), 2)
        self.assertEqual(get_response_data[0]['name'], new_category_name_1)
        self.assertEqual(get_response_data[1]['name'], new_category_name_2)

    def test_update_existing_category(self):
        """
        Ensure we can update the name for an existing category
        """
        create_user_response = self.create_user(self.test_username, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name_1 = 'soup'
        post_response_1 = self.create_category(new_category_name_1)
        self.assertEqual(post_response_1.status_code, status.HTTP_201_CREATED)
        post_response_data_1 = json.loads(post_response_1.get_data(as_text=True))
        new_category_url = post_response_data_1['url']
        new_category_name_2 = 'soup 2'
        data = {'name': new_category_name_2}
        put_response = self.test_client.put(
            new_category_url,
            headers=self.get_authentication_headers(self.test_username, self.test_user_password),
            data=json.dumps(data)
        )
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        get_response = self.test_client.get(
            new_category_url,
            headers=self.get_authentication_headers(self.test_username, self.test_user_password)
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['name'], new_category_name_2)

    def create_recipe(self, title, body, category):
        """
        create a recipe item
        """
        url = url_for('api.recipelistresource', _external=True)
        data = {'title': title, 'body': body, 'category': category}
        response = self.test_client.post(
            url,
            headers=self.get_authentication_headers(self.test_username, self.test_user_password),
            data=json.dumps(data)
        )
        return response

    def test_create_and_retrieve_recipe(self):
        """
        Ensure we can create a new message and then retrieves it
        """
        create_user_response = self.create_user(self.test_username, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_recipe_title = 'Welcome to the recipe world'
        new_recipe_body = 'This is the beginning of your hunger-free life'
        new_recipe_category = 'Soup'
        post_response = self.create_recipe(new_recipe_title, new_recipe_body, new_recipe_category)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.query.count(), 1)
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['title'], new_recipe_title)
        new_recipe_url = post_response_data['url']
        get_response = self.test_client.get(
            new_recipe_url,
            headers=self.get_authentication_headers(self.test_username, self.test_user_password)
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['title'], new_recipe_title)
        self.assertEqual(get_response_data['body'], new_recipe_body)
        self.assertEqual(get_response_data['category']['name'], new_recipe_category)

    def test_create_duplicated_recipe(self):
        """
        Ensure we can not create a duplicated recipe
        """
        create_user_response = self.create_user(self.test_username, self.test_user_password)
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_recipe_title = 'Welcome to the recipe world'
        new_recipe_body = 'This is the beginning of your hunger-free life'
        new_recipe_category = 'Soup'
        post_response = self.create_recipe(new_recipe_title, new_recipe_body, new_recipe_category)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.wuery.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['title'], new_recipe_title)
        self.assertEqual(post_response_data['body'], new_recipe_body)
        new_recipe_url = post_response_data['url']
        get_response = self.test_client.get(
            new_recipe_url,
            headers=self.get_authentication_headers(self.test_username, self.test_user_password)
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['title'], new_recipe_title)
        self.assertEqual(get_response_data['body'], new_recipe_body)
        self.assertEqual(get_response_data['category']['name'], new_recipe_category)
        second_post_response = self.create_recipe(new_recipe_title, new_recipe_body, new_recipe_category)
        self.assertEqual(second_post_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Recipe.query.count(), 1)
