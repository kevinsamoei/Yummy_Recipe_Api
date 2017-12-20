# coding=utf-8
from flask import redirect
from app import create_app

app = create_app('config')
app.config["Swagger"] = {
    "title": "Yummy Recipe App",
    "uiversion": 2,
}


@app.route('/')
def home():
    return redirect('apidocs')


if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
