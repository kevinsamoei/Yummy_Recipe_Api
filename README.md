# Yummy_Recipe_Api
Yummy recipes provides a platform for users to keep track of their awesome recipes and share with others if they so wish.

[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)  [![Build Status](https://travis-ci.org/kevinsamoei/Yummy_Recipe_Api.svg?branch=develop)](https://travis-ci.org/kevinsamoei/Yummy_Recipe_Api)  [![Coverage Status](https://coveralls.io/repos/github/kevinsamoei/Yummy_Recipe_Api/badge.svg?branch=develop&service=github)](https://coveralls.io/github/kevinsamoei/Yummy_Recipe_Api?branch=develop)  [![Maintainability](https://api.codeclimate.com/v1/badges/586d92d364bfd5ccd26b/maintainability)](https://codeclimate.com/github/kevinsamoei/Yummy_Recipe_Api/maintainability)  [![Codacy Badge](https://api.codacy.com/project/badge/Grade/04b5b7f72b494b98975830bdadf1edf1)](https://www.codacy.com/app/kevinsamoei/Yummy_Recipe_Api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kevinsamoei/Yummy_Recipe_Api&amp;utm_campaign=Badge_Grade)  [![Code Health](https://landscape.io/github/kevinsamoei/Yummy_Recipe_Api/develop/landscape.svg?style=plastic)](https://landscape.io/github/kevinsamoei/Yummy_Recipe_Api/develop)
# API Endpoints

URL Endpoint	|               HTTP requests   | access| status|
----------------|-----------------|-------------|------------------
/api/auth/register/   |      POST	| Register a new user|public
/api/auth/login/	  |     POST	| Login and retrieve token|public
/api/categories/	              |      POST	|  Create a new recipe category|private
/api/categories	              |      GET	|  Retrieve all categories  for user|private
/api/categories/<_id>/   |  	 GET	   | Retrieve a category by ID | private
/api/categories/<_id>/	  |      PUT	|     Update a category |private
/api/categories/<_id>/   |      DELETE	| Delete a category |private
/api/recipes/  |  GET  |Retrieve recipes in a given category |private
/api/recipes/     |     POST	| Create recipes in a category|private
/api/recipes/<_id>/|	DELETE	| Delete a recipe in a category  |private
/api/recipes/<_id>/ |	PUT   	|update recipe details |private
