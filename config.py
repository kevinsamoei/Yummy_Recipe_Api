# coding=utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
PORT = 5000
HOST = "127.0.0.1"
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
# SQLALCHEMY_DATABASE_URI = "postgresql://postgres:kevin5445@localhost/recipe"
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
# SQLALCHEMY_DATABASE_URI = "postgres://haxtmfgwuarmyb:490a8f39e81eaaa693a5bae6766b73fa8c70eb736d3ce25a0cd451b9b268a041@ec2-54-235-148-19.compute-1.amazonaws.com:5432/d63ojr69or0a1l"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
PAGINATION_PAGE_SIZE = 5
PAGINATION_PAGE_ARGUMENT_NAME = 'page'
