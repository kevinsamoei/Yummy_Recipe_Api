# Yummy_Recipe_Api
Yummy recipes provides a platform for users to keep track of their awesome recipes and share with others if they so wish.

[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)  [![Build Status](https://travis-ci.org/kevinsamoei/Yummy_Recipe_Api.svg?branch=develop)](https://travis-ci.org/kevinsamoei/Yummy_Recipe_Api)  [![Coverage Status](https://coveralls.io/repos/github/kevinsamoei/Yummy_Recipe_Api/badge.svg?branch=develop&service=github)](https://coveralls.io/github/kevinsamoei/Yummy_Recipe_Api?branch=develop)  [![Maintainability](https://api.codeclimate.com/v1/badges/586d92d364bfd5ccd26b/maintainability)](https://codeclimate.com/github/kevinsamoei/Yummy_Recipe_Api/maintainability)  [![Codacy Badge](https://api.codacy.com/project/badge/Grade/04b5b7f72b494b98975830bdadf1edf1)](https://www.codacy.com/app/kevinsamoei/Yummy_Recipe_Api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kevinsamoei/Yummy_Recipe_Api&amp;utm_campaign=Badge_Grade)  [![Code Health](https://landscape.io/github/kevinsamoei/Yummy_Recipe_Api/develop/landscape.svg?style=plastic)](https://landscape.io/github/kevinsamoei/Yummy_Recipe_Api/develop)

# Overview
# What?
Yummy recipes provides a platform for users to keep track of their awesome recipes and share with others if they so wish.

# How?
This project is broken down into 4 challenges whose completion would contribute greatly to your learning towards becoming a full-stack developer. Upon completion, you would have built a world-class full-stack (frontend and backend)  Python application.

# Why?
Andela distributes opportunities. We disseminate Learning and catalyse Technology leadership. The project is founded on the premise that aspiring Technology Leaders learn programming whilst building things that matter and that the best way to learn is by building a complete product.  

`This project has one objective: create opportunities for learning where they build real products. In this way, we inspire change in the African tech landscape.`
# Usage
* Users create accounts
* Users can log in
* Users create, view, update and delete recipe categories
* Users can create, view, update or delete recipes in existing categories


# API Endpoints
 ### Authentication
 
URL Endpoint	|               HTTP requests   | access| Public access|
----------------|-----------------|-------------|------------------
POST /api/auth/register/   |      POST	| Register a new user|TRUE
POST /api/auth/login/	  |     POST	| Login and retrieve token|TRUE
POST /api/auth/logout/	  |     POST	| Logout a user and revoke access|TRUE
POST /api/auth/reset-password/	  |     POST	| Reset a user's password|TRUE

 ### Categories

URL Endpoint	|               HTTP requests   | access| Public access|
----------------|-----------------|-------------|------------------
POST /api/categories/   |      POST	| Create a new category|FALSE
GET /api/categories/	  |     GET	| Retrieve a paginated list of categories|FALSE
GET /api/categories/\<id>	  |     GET	| Retrieve a category with the specified id|FALSE
PUT /api/categories/\<id>	  |     PUT	| Edit a category|FALSE
DELETE /api/categories/\<id>	  |     PUT	| Delete a category|FALSE

### Recipes

URL Endpoint	|               HTTP requests   | access| Public access|
----------------|-----------------|-------------|------------------
POST /api/recipes/   |      POST	| Create a new recipe|FALSE
GET /api/recipes/	  |     GET	| Retrieve a paginated list of recipes|FALSE
GET /api/recipes/\<id>	  |     GET	| Retrieve a recipe with the specified id|FALSE
PUT /api/recipes/\<id>	  |     PUT	| Edit a recipe|FALSE
DELETE /api/recipes/\<id>	  |     PUT	| Delete a recipe|FALSE
