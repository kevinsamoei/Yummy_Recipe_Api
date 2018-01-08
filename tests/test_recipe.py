import unittest
import json
from flask import url_for
from models import Category, Recipe, db
from api import status
from app import create_app


class RecipeCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app("test_config")
        # initialize the test client
        self.client = self.app.test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        self.test_username = 'kevin'
        self.test_user_password = 'P@ssword1'
        # This is the user test json data with a predefined email and password
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

    def create_recipe(self, title, body, category):
        """
        create a recipe item
        """
        self.create_user(self.test_username,
                         self.test_user_password)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        url = url_for('api.recipelistresource', _external=True)
        data = {"title": title, "body": body, "category": category}
        response = self.test_client.post(
            url,
            headers={"x-access-token": access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        return response

    def test_create_and_retrieve_recipe(self):
        """
        Ensure we can create a new message and then retrieves it
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code, 201)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        new_recipe_title = "Recipe"
        new_recipe_body = "This is the beginning of your hunger free life"
        new_recipe_category = "Soup"
        post_response = self.create_recipe(new_recipe_title,
                                           new_recipe_body,
                                           new_recipe_category)
        self.assertEqual(post_response.status_code, 201)
        self.assertEqual(Recipe.query.count(), 1)
        self.assertEqual(Category.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['title'], new_recipe_title)
        new_recipe_url = post_response_data['url']
        get_response = self.test_client.get(
            new_recipe_url,
            headers={"x-access-token": access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['title'],
                         new_recipe_title)
        self.assertEqual(get_response_data['body'],
                         new_recipe_body)
        self.assertEqual(get_response_data['category']['name'],
                         new_recipe_category)

    def test_create_duplicated_recipe(self):
        """
        Ensure we can not create a duplicated recipe
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        new_recipe_title = 'Recipe World'
        new_recipe_body = 'This is the beginning of your hunger-free life'
        new_recipe_category = 'Soup'
        post_response = self.create_recipe(new_recipe_title,
                                           new_recipe_body,
                                           new_recipe_category)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['title'], new_recipe_title)
        self.assertEqual(post_response_data['body'], new_recipe_body)
        new_recipe_url = post_response_data['url']
        get_response = self.test_client.get(
            new_recipe_url,
            headers={"x-access-token":access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['title'],
                         new_recipe_title)
        self.assertEqual(get_response_data['body'],
                         new_recipe_body)
        self.assertEqual(get_response_data['category']['name'],
                         new_recipe_category)
        second_post_response = self.create_recipe(new_recipe_title,
                                                  new_recipe_body,
                                                  new_recipe_category)
        self.assertEqual(second_post_response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Recipe.query.count(), 1)

    def test_retrieve_recipe_list(self):
        """
        Ensure we can retrieve the recipes paginated list
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        get_first_page_url_1 = url_for('api.recipelistresource',
                                       _external=True)
        get_first_page_response_1 = self.test_client.get(
            get_first_page_url_1,
            headers={"x-access-token": access_token}
        )
        res = json.loads(get_first_page_response_1.data.decode())
        self.assertEqual(res, {"Error": "No recipes. Create a recipe!"})
        new_recipe_title1 = 'Recipe World'
        new_recipe_body1 = 'This is the beginning of your hunger-free life'
        new_recipe_category1 = 'Soup'
        post_response = self.create_recipe(new_recipe_title1,
                                           new_recipe_body1,
                                           new_recipe_category1)
        self.assertEqual(post_response.status_code,
                         status.HTTP_201_CREATED)
        self.assertEqual(Recipe.query.count(), 1)
        new_recipe_title2 = 'Meat Soup'
        new_recipe_body2 = 'This is the beginning of your hunger-free life'
        new_recipe_category2 = 'Breakfast'
        post_response = self.create_recipe(new_recipe_title2,
                                           new_recipe_body2,
                                           new_recipe_category2)
        self.assertEqual(post_response.status_code,
                         status.HTTP_201_CREATED)
        self.assertEqual(Recipe.query.count(), 2)
        get_first_page_url = url_for('api.recipelistresource',
                                     _external=True)
        get_first_page_response = self.test_client.get(
            get_first_page_url,
            headers={"x-access-token": access_token}
            )
        get_first_page_response_data = json.loads(
            get_first_page_response.get_data(as_text=True))
        self.assertEqual(get_first_page_response.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(get_first_page_response_data['count'], 2)
        self.assertIsNone(get_first_page_response_data['previous'])
        self.assertIsNone(get_first_page_response_data['next'])
        self.assertIsNotNone(get_first_page_response_data['results'])
        self.assertEqual(len(get_first_page_response_data['results']), 2)
        self.assertEqual(get_first_page_response_data['results'][0]['title'],
                         new_recipe_title1)
        self.assertEqual(get_first_page_response_data['results'][1]['title'],
                         new_recipe_title2)
        get_second_page_url = url_for('api.recipelistresource', page=2)
        get_second_page_response = self.test_client.get(
            get_second_page_url,
            headers={"x-access-token": access_token}
        )
        get_second_page_response_data = json.loads(
            get_second_page_response.get_data(as_text=True))
        self.assertEqual(get_second_page_response.status_code,
                         status.HTTP_200_OK)
        # self.assertIsNotNone(get_second_page_response_data['previous'])
        self.assertEqual(get_second_page_response_data,
                         {"Error": "No recipes. Create a recipe!"})
        # self.assertIsNone(get_second_page_response_data['next'])
        # self.assertIsNotNone(get_second_page_response_data['results'])
        # self.assertEqual(len(get_second_page_response_data['results']), 0)

    def test_update_recipe(self):
        """
        Ensure we can update a single field for an existing message
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        new_recipe_title_1 = 'Welcome'
        new_recipe_body_1 = 'This is the body'
        new_recipe_category_1 = 'soup'
        post_response = self.create_recipe(new_recipe_title_1,
                                           new_recipe_body_1,
                                           new_recipe_category_1)
        self.assertEqual(post_response.status_code,
                         status.HTTP_201_CREATED)

        self.assertEqual(Recipe.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        new_recipe_url = post_response_data['url']
        new_recipe_title = "Meat Soup"
        data = {'title': new_recipe_title}
        patch_response = self.test_client.put(
            new_recipe_url,
            headers={"x-access-token": access_token},
            data=json.dumps(data)
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        new_recipe_title_2 = 'Welcome'
        new_recipe_body_2 = 'This is the body'
        new_recipe_category_2 = 'soup'
        post_response_2 = self.create_recipe(new_recipe_title_2,
                                             new_recipe_body_2,
                                             new_recipe_category_2)
        self.assertEqual(post_response_2.status_code, 201)
        new_recipe_title_3 = 'Welcome'
        data_2 = {'title': new_recipe_title_3}
        patch_response_2 = self.test_client.put(
            new_recipe_url,
            headers={"x-access-token": access_token},
            data=json.dumps(data_2),
            content_type='application/json'
        )
        res = json.loads(patch_response_2.data.decode())
        self.assertEqual(res, {'error': 'A recipe with the same title already exists'})
        get_response = self.test_client.get(
            new_recipe_url,
            headers={"x-access-token": access_token})
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['title'],
                         new_recipe_title)

    def test_delete_recipe(self):
        """
        Test a recipe is successfully Deleted
        """
        create_user_response = self.create_user(self.test_username,
                                                self.test_user_password)
        self.assertEqual(create_user_response.status_code,
                         status.HTTP_201_CREATED)
        result = self.login_user(
            self.test_username, self.test_user_password)
        access_token = json.loads(result.data.decode())['token']
        new_recipe_title_1 = 'Welcome'
        new_recipe_body_1 = 'This is the body'
        new_recipe_category_1 = 'soup'
        post_response = self.create_recipe(new_recipe_title_1,
                                           new_recipe_body_1,
                                           new_recipe_category_1)
        self.assertEqual(post_response.status_code,
                         status.HTTP_201_CREATED)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        new_recipe_url = post_response_data['url']
        delete_response = self.test_client.delete(
            new_recipe_url,
            headers={"x-access-token":access_token}
            )
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
