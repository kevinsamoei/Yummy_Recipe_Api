# coding=utf-8
import jwt

from flask import request, jsonify, make_response
from functools import wraps
from models import User, DisableTokens


def token_required(f):
    """
    Define authentication based on the auth token
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 401)

        try:
            data = jwt.decode(token, 'topsecret')
            is_blacklisted_token = DisableTokens.check_blacklist(token)
            if is_blacklisted_token:
                return make_response(jsonify({'message': 'Logged out. log in again'}), 401)
            else:
                current_user = User.query.filter_by(username=data['username']).first()
        except:
            return make_response(jsonify({'message': 'Token is Invalid'}), 401)

        return f(current_user, *args, **kwargs)
    return decorated
