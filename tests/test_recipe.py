import json
from api.models import Recipe
from api import status
from .base_tests import BaseTestCase


class RecipeCase(BaseTestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        super(RecipeCase, self).setUp()
        self.url = 'api/category/1/recipes/'
        self.recipe_url = 'api/recipes/1'
        self.register = self.client.post('api/auth/register/', data=json.dumps(self.user_data),
                                         content_type='application/json')
        self.login_response = self.login_user(self.test_username, self.test_user_password)
        self.access_token = json.loads(self.login_response.data.decode())['token']
        self.recipe_title = "recipe"
        self.recipe_body = "This is the beginning of your hunger free life"
        self.create_response = self.create_recipe(self.recipe_title, self.recipe_body)
        self.category = self.create_category(self.category_name)
        self.category_url = 1

    def create_recipe(self, title, body):
        """
        create a recipe item
        """
        data = {"title": title, "body": body}
        response = self.test_client.post(
            self.url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        return response

    def create_category(self, name):
        data = {'name': name}
        response = self.test_client.post(
            self.category_url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        return response

    def test_create_recipe(self):
        """
        Ensure we can create a new message and then retrieves it
        """
        new_recipe_title = "meat"
        new_recipe_body = "This is the beginning of your hunger free life"
        data = {"title": new_recipe_title, "body": new_recipe_body}
        post_response = self.test_client.post(
            self.url,
            headers={"x-access-token": self.access_token},
            data=json.dumps(data),
            content_type='application/json'
        )
        post_response_data = json.loads(post_response.get_data(as_text=True))
        print(post_response_data)
        self.assertEqual(post_response.status_code, 201)
        self.assertEqual(Recipe.query.count(), 1)

    def test_retrieve_recipe(self):
        """Test a user can retrieve a created recipe"""
        self.create_recipe(self.recipe_title, self.recipe_body)
        get_response = self.test_client.get(
            self.recipe_url,
            headers={"x-access-token": self.access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        print(get_response_data)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data['title'],
                         self.recipe_title)

    def test_retrieve_recipe_not_found(self):
        """Retrieve a recipe that does not exist"""
        get_response = self.test_client.get(
            '/api/recipes/20',
            headers={"x-access-token": self.access_token}
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response_data, {'Error': 'A recipe with Id 20 does not exist'})
        self.assertEqual(get_response.status_code, 404)

    def test_create_existing_recipe(self):
        """Create an existing recipe"""
        self.create_recipe(self.recipe_title, self.recipe_body)
        data = {"title": self.recipe_title, "body": self.recipe_body}
        response = self.test_client.post(
            self.url,
            data=json.dumps(data),
            headers={"x-access-token": self.access_token},
            content_type='application/json'
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response_data['message'], 'A recipe with the same title already exists')

    def test_create_recipe_with_no_data(self):
        """Create recipe with no data provided"""
        data = {}
        post_response = self.test_client.post(
            self.url,
            data=json.dumps(data),
            headers={"x-access-token": self.access_token},
            content_type='application/json'
        )
        post_response_data = json.loads(post_response.data.decode())
        self.assertEqual(post_response_data, {"message": "No output data provided"})
        self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_missing_data(self):
        """Missing one required data"""
        data = {"title": "meat"}
        post_response = self.test_client.post(
            self.url,
            data=json.dumps(data),
            headers={"x-access-token": self.access_token},
            content_type='application/json'
        )
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data['message'], {'body': ['Missing data for required field.']})
        self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recipe_with_invalid_title(self):
        """Recipe with invalid recipe title"""
        data = {"title": "      ", "body": self.recipe_body}
        response = self.test_client.post(
            self.url,
            data=json.dumps(data),
            headers={"x-access-token": self.access_token},
            content_type='application/json'
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, {'message': 'No input data provided'})
        self.assertEqual(response.status_code, 400)

    def test_create_recipe_with_invalid_body(self):
        """Recipe with invalid recipe body"""
        data = {"title": "kevin", "body": "        "}
        response = self.test_client.post(
            self.url,
            data=json.dumps(data),
            headers={"x-access-token": self.access_token},
            content_type='application/json'
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, {'message': 'No input data provided'})
        self.assertEqual(response.status_code, 400)

    def test_retrieve_recipe_list(self):
        """
        Ensure we can retrieve the recipes paginated list
        """
        new_recipe_title = 'meat soup'
        new_recipe_body = self.recipe_body
        self.create_recipe(new_recipe_title,
                           new_recipe_body)
        get_first_page_response = self.test_client.get(
            self.url,
            headers={"x-access-token": self.access_token}
            )
        get_first_page_response_data = json.loads(
            get_first_page_response.get_data(as_text=True))
        print(get_first_page_response_data)
        self.assertEqual(get_first_page_response.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(get_first_page_response_data['count'], 1)

    def test_retrieve_search_not_found(self):
        """Search a category not there"""
        url = 'api/category/1/recipes/?q=git'
        response = self.test_client.get(
            url,
            headers={"x-access-token": self.access_token}
        )
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data, {'error': 'No recipe found for that search.'})

    def test_search_existing_recipe(self):
        """Test search for a recipe"""
        self.create_recipe(self.recipe_title, self.recipe_body)
        url = 'api/category/1/recipes/?q=recipe'
        response = self.test_client.get(
            url,
            headers={"x-access-token": self.access_token}
        )
        response_data = json.loads(response.get_data(as_text=True))
        print(response_data)
        self.assertEqual(response_data['results'][0]['title'], self.recipe_title)

    def test_update_recipe(self):
        """
        Ensure we can update a single field for an existing message
        """
        self.create_recipe(self.recipe_title, self.recipe_body)
        new_recipe_title = "meat soup"
        data = {'title': new_recipe_title}
        patch_response = self.test_client.put(
            'api/recipes/1',
            headers={"x-access-token": self.access_token},
            data=json.dumps(data)
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

    def test_update_with_non_recipe(self):
        """Test update a recipe that does not exist"""
        url = '/api/recipes/10'
        data = {"title": self.recipe_title, "body": self.recipe_body}
        res = self.test_client.put(
            url,
            data=json.dumps(data),
            headers={"x-access-token": self.access_token},
            content_type='application/json'

        )
        res_data = json.loads(res.get_data(as_text=True))
        self.assertEqual(res_data, {'Error': 'A recipe with that Id does not exist'})

    def test_delete_recipe(self):
        """
        Test a recipe is successfully Deleted
        """
        self.create_recipe(self.recipe_title, self.recipe_body)
        delete_response = self.test_client.delete(
            self.recipe_url,
            headers={"x-access-token": self.access_token}
            )
        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)

    def test_delete_recipe_not_there(self):
        """Test delete a non existent recipe"""
        url = '/api/recipes/4'
        delete_response = self.test_client.delete(
            url,
            headers={"x-access-token": self.access_token}
        )
        delete_response_data = json.loads(delete_response.get_data(as_text=True))
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(delete_response_data, {"error": "A recipe with the the id of 4 does not exist"})
