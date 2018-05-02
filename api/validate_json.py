from functools import wraps
from flask import request


from werkzeug.exceptions import BadRequest


def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            request.json
        except BadRequest as e:
            msg = "payload must be a valid json"
            response = {"error": msg}
            return response, 400
        return f(*args, **kw)
    return wrapper
