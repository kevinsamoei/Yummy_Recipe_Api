# coding=utf-8
import os
from flask import redirect
from app import create_app
from flask_mail import Mail


app = create_app('config')


app.config.update(
    DEBUG=True,
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
)
mail = Mail(app)


@app.route('/')
def home():
    return redirect('apidocs')


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
