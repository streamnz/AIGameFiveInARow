from flask import Blueprint, request, jsonify, session

from service.user_service import UserService
from service.verification_service import VerificationService
from utils.jwt_util import create_jwt_token, token_required

user_controller = Blueprint('user_controller', __name__)
user_service = UserService()
verification_service = VerificationService()


# Send email verification code
@user_controller.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    """发送邮箱验证码"""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    # 检查邮件服务是否可用
    if not verification_service.is_email_service_enabled():
        return jsonify({
            "status": "error", 
            "message": "Email verification service is not available. Please contact support."
        }), 503

    # 检查邮箱格式
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"status": "error", "message": "Invalid email format."}), 400

    # 检查邮箱是否已被注册
    existing_user = user_service.get_user_by_email(email)
    if existing_user:
        return jsonify({"status": "error", "message": "Email is already registered."}), 400

    # 发送验证码
    result = verification_service.send_verification_code(email)
    
    if result["status"] == "success":   
        return jsonify(result), 200
    else:
        return jsonify(result), 400


# Verify email verification code
@user_controller.route('/verify-email-code', methods=['POST'])
def verify_email_code():
    """验证邮箱验证码"""
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return jsonify({"status": "error", "message": "Email and verification code are required."}), 400

    # 验证验证码
    result = verification_service.verify_code(email, code)
    
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 400


# User registration
@user_controller.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    email_verified = data.get('emailVerified', False)

    if not username:
        return jsonify({"status": "error", "message": "Username is required."}), 400

    if not password:
        return jsonify({"status": "error", "message": "Password is required."}), 400

    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    # 如果启用了邮箱验证，检查邮箱是否已验证
    if verification_service.is_email_service_enabled() and not email_verified:
        return jsonify({
            "status": "error", 
            "message": "Email verification is required before registration."
        }), 400

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

    # 模拟固定用户信息
    # if email == "hao@gmail.com":
    #     login_result = {
    #         "status": "success",
    #         "user": {
    #             "id": 1,
    #             "username": "hao",
    #             "email": "hao@gmail.com"
    #         }}
    # else:
    #     return jsonify({"status": "error", "message": "Bad username or password"}), 401

    cur_user = login_result.get("user")

    access_token = create_jwt_token(cur_user.id, cur_user.username, cur_user.email)
    # access_token = create_jwt_token(cur_user["id"], cur_user["username"], cur_user["email"])

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


# Get verification status (optional endpoint for debugging)
@user_controller.route('/verification-status', methods=['POST'])
def get_verification_status():
    """获取邮箱验证状态（可选的调试接口）"""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    status = verification_service.get_verification_status(email)
    status.update({
        "email_service_enabled": verification_service.is_email_service_enabled()
    })
    
    return jsonify({"status": "success", "verification_status": status}), 200


@user_controller.route('/base/health', methods=['GET'])
def health_check():
    return jsonify({"status": "success", "message": "Service is running healthy."}), 200


# 钱包相关接口

@user_controller.route('/bind-wallet', methods=['POST'])
@token_required
def bind_wallet():
    """绑定钱包地址"""
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    wallet_type = data.get('wallet_type', 'metamask')

    if not wallet_address:
        return jsonify({"status": "error", "message": "Wallet address is required."}), 400

    # 从JWT token中获取用户ID
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        from utils.jwt_util import jwt, SECRET_KEY
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('id')
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid token."}), 401

    # 绑定钱包
    result = user_service.bind_wallet(user_id, wallet_address, wallet_type)
    
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@user_controller.route('/unbind-wallet', methods=['POST'])
@token_required
def unbind_wallet():
    """解绑钱包地址"""
    # 从JWT token中获取用户ID
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        from utils.jwt_util import jwt, SECRET_KEY
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('id')
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid token."}), 401

    # 解绑钱包
    result = user_service.unbind_wallet(user_id)
    
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@user_controller.route('/wallet-info', methods=['GET'])
@token_required
def get_wallet_info():
    """获取用户钱包信息"""
    # 从JWT token中获取用户ID
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        from utils.jwt_util import jwt, SECRET_KEY
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('id')
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid token."}), 401

    # 获取钱包信息
    result = user_service.get_user_wallet_info(user_id)
    
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 400
