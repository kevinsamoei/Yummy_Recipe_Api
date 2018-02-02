# coding=utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
# PORT = 5000
# HOST = "127.0.0.1"
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
# SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
PAGINATION_PAGE_SIZE = 5
PAGINATION_PAGE_ARGUMENT_NAME = 'page'
SECRET_KEY = "Thisistopsecretstuff"
# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_PORT = 465
# MAIL_USERNAME = "samoeikev@gmail.com"
# MAIL_PASSWORD = "s@moei5445"
# MAIL_USE_TLS = True
# MAIL_USE_SSL = True
