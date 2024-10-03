from flask import Blueprint, request, jsonify, session

from service.user_service import UserService
from utils.jwt_util import create_jwt_token, token_required

user_controller = Blueprint('user_controller', __name__)
user_service = UserService()


# User registration
@user_controller.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username:
        return jsonify({"status": "error", "message": "Username is required."}), 400

    if not password:
        return jsonify({"status": "error", "message": "Password is required."}), 400

    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    registration_result = user_service.register_user(username, password, email)
    if registration_result["status"] == "error":
        return jsonify(registration_result), 400

    ## login process
    cur_user = registration_result.get("user")
    access_token = create_jwt_token(cur_user.id, cur_user.username, cur_user.email)
    session[cur_user.email] = access_token

    return jsonify({"status": "success", "message": "User registered successfully.", "access_token": access_token})


# User login
@user_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('username')
    password = data.get('password')

    if not email or not password:
        return jsonify({"status": "error", "message": "Username and password are required."}), 400

    login_result = user_service.login_user(email, password)
    if login_result["status"] == "error":
        return jsonify({"msg": "Bad username or password"}), 401

    cur_user = login_result.get("user")

    access_token = create_jwt_token(cur_user.id, cur_user.username, cur_user.email)

    session[email] = access_token

    print("access_token:{}", access_token)
    return jsonify(access_token=access_token), 200


# Logout
@user_controller.route('/logout', methods=['POST'])
@token_required
def logout():
    data = request.get_json()
    email = data.get('email')
    session.pop(email, None)
    return jsonify({"status": "success", "message": "Logged out successfully."})


# Get leaderboard
@user_controller.route('/leaderboard', methods=['GET'])
@token_required
def leaderboard():
    leaderboard = user_service.get_leaderboard()
    return jsonify({"status": "success", "leaderboard": leaderboard})
