# coding=utf-8
import os
from flask import redirect
from app import create_app
from flask_mail import Mail, Message


app = create_app('config')

# mail = Mail(app)

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='samoeikev@gmail.com',
    MAIL_PASSWORD='s@moei5445'
)
mail = Mail(app)


@app.route('/')
def home():
    return redirect('apidocs')


@app.route('/send-mail/')
def send_mail():
    try:
        msg = Message("Send Mail Tutorial!",
                      sender="samoeikev@gmail.com",
                      recipients=["kevin.samoei@andela.com"])
        msg.body = "Yo!\nHave you heard the good word of Python???"
        mail.send(msg)
        return 'Mail sent!'
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(
            debug=app.config['DEBUG'])
