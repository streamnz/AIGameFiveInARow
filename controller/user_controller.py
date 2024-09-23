from flask import Blueprint, request, jsonify, session
from service.user_service import UserService

user_controller = Blueprint('user_controller', __name__)
user_service = UserService()


# User registration
@user_controller.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required."}), 400

    registration_result = user_service.register_user(username, password)
    if registration_result["status"] == "error":
        return jsonify(registration_result), 400

    return jsonify({"status": "success", "message": "User registered successfully."})


# User login
@user_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required."}), 400

    login_result = user_service.login_user(username, password)
    if login_result["status"] == "error":
        return jsonify(login_result), 400

    # Store user in session
    session['user'] = username
    return jsonify({"status": "success", "message": "Login successful."})


# Logout
@user_controller.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"status": "success", "message": "Logged out successfully."})


# Get leaderboard
@user_controller.route('/leaderboard', methods=['GET'])
def leaderboard():
    leaderboard = user_service.get_leaderboard()
    return jsonify({"status": "success", "leaderboard": leaderboard})