# Yummy_Recipe_Api  :smiley:
Yummy recipes provides a platform for users to keep track of their awesome recipes and share with others if they so wish.

[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)  [![Build Status](https://travis-ci.org/kevinsamoei/Yummy_Recipe_Api.svg?branch=develop)](https://travis-ci.org/kevinsamoei/Yummy_Recipe_Api)  [![Coverage Status](https://coveralls.io/repos/github/kevinsamoei/Yummy_Recipe_Api/badge.svg?branch=develop&service=github)](https://coveralls.io/github/kevinsamoei/Yummy_Recipe_Api?branch=develop)  [![Maintainability](https://api.codeclimate.com/v1/badges/586d92d364bfd5ccd26b/maintainability)](https://codeclimate.com/github/kevinsamoei/Yummy_Recipe_Api/maintainability)  [![Codacy Badge](https://api.codacy.com/project/badge/Grade/04b5b7f72b494b98975830bdadf1edf1)](https://www.codacy.com/app/kevinsamoei/Yummy_Recipe_Api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kevinsamoei/Yummy_Recipe_Api&amp;utm_campaign=Badge_Grade)  [![Code Health](https://landscape.io/github/kevinsamoei/Yummy_Recipe_Api/develop/landscape.svg?style=plastic)](https://landscape.io/github/kevinsamoei/Yummy_Recipe_Api/develop)

# Overview
# What?
Yummy recipes provides a platform for users to keep track of their awesome recipes and share with others if they so wish.
# Usage
* Users create accounts
* Users can log in
* Users create, view, update and delete recipe categories
* Users can create, view, update or delete recipes in existing categories

# Important Links
- [Heroku](http://yummyrecipesapi.herokuapp.com/apidocs/)
- [Github](https://github.com/kevinsamoei/Yummy_Recipe_Api)
- [Licene](https://opensource.org/licenses/mit-license.php)

# Prerequisities
The following software is needed for the project:
- Python 3.XX
- Flask
- Postman(optional)

# Installing
Follow this steps to get you up and running:
* Install python
#### Install Python: Windows
Download python for windows on [Official python website](https://www.python.org/downloads/windows/) and run the executable file

#### Install Python: OS X
You need to go to the [website](https://www.python.org/downloads/release/python-363/) and download the Python installer and run the file.
#### Install python: linux
On the command line run ```$ sudo apt-get install python3.6```
#### Install the project locally
* Clone the project

  `git clone https://github.com/kevinsamoei/Yummy_Recipe_Api`
* Move into the project's folder

  `cd Yummy_Recipe_Api`
* Install virtual environment and Create a virtual environment

    `pip install virtualenv`
* create a virtual environment called "myenv"

   `$ python3 -m venv myvenv`
* Activate your virtual environment

  `source myvenv/bin/activate`

* Install project requirements
   `(myvenv) ~$ pip install -r requirements.txt`
 
* Create your postgresql database and change the uri in the `config.py` module

* Run the application
    `(myvenv) ~$ python run.py`

# Running the tests
To run the tests use either pytests or nosetests:
   ```pytest --cov=api tests/```
   ```nosetests --with-coverage --cover-tests --cover-erase --cover-package=api```

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
DELETE /api/categories/\<id>	  |     DELETE	| Delete a category|FALSE

### Recipes

URL Endpoint	|               HTTP requests   | access| Public access|
----------------|-----------------|-------------|------------------
POST /api/recipes/   |      POST	| Create a new recipe|FALSE
GET /api/recipes/	  |     GET	| Retrieve a paginated list of recipes|FALSE
GET /api/recipes/\<id>	  |     GET	| Retrieve a recipe with the specified id|FALSE
PUT /api/recipes/\<id>	  |     PUT	| Edit a recipe|FALSE
DELETE /api/recipes/\<id>	  |     DELETE	| Delete a recipe|FALSE


# Built with
* Python 3.6
* Flask 0.12.2
* Flask-RestFul
* Postgresql

# Authors
* Kevin samoei :hearts:

# Licence 
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/kevinsamoei/Yummy_Recipe_Api/blob/develop/LICENSE) file for details

# Acknowledgements
* Andelans
* Stack overflow
* Official documentations for python, flask, postgresql