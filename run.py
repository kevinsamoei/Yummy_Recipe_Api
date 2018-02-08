# coding=utf-8
import os
from flask import redirect
from app import create_app

app = create_app('config')


@app.route('/')
def home():
    return redirect('apidocs')


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
