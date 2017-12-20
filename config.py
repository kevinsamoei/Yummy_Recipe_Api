# coding=utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
PORT = 5000
HOST = "127.0.0.1"
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:kevin5445@localhost/recipe"
#SQLALCHEMY_DATABASE_URI = "postgres://ddcvhkdjzkhvgd:4a7346504fa1d6a893dfabfbea45120d6edbd1a5de7b346cc4db2bd750ca5208@ec2-23-21-231-58.compute-1.amazonaws.com:5432/d79rl79op585ce"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
PAGINATION_PAGE_SIZE = 5
PAGINATION_PAGE_ARGUMENT_NAME = 'page'
