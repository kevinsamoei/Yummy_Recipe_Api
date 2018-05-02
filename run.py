# coding=utf-8
import os
from flask import redirect
from app import create_app
from flask_cors import CORS

app = create_app('config')

CORS(app)


@app.route('/')
def home():
    return redirect('apidocs')


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
