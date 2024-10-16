import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from jwt import ExpiredSignatureError, InvalidTokenError

# 密钥用于签名 JWT
SECRET_KEY = "abc_def_ghi"


def create_jwt_token(user_id, username, email):
    payload = {
        'id': user_id,
        'username': username,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Token 过期时间
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从请求的头部获取 token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        # 如果没有找到 token，返回错误
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # 解码 token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['username']  # 例如从token中获取username
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated


# 从请求中提取 token，并进行解码
def get_decoded_token_from_request():
    try:
        token = request.args.get('token')  # 从请求参数中获取 token
        if not token:
            raise Exception("Token is missing in request")

        decoded_token = decode_jwt_token(token)
        return decoded_token
    except Exception as e:
        raise Exception(f"Error decoding token: {str(e)}")


# 解码 JWT token 并返回解码后的 payload
def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except ExpiredSignatureError:
        raise Exception("Token has expired")
    except InvalidTokenError:
        raise Exception("Invalid token")
