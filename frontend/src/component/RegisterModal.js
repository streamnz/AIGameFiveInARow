import React, { useState } from 'react';
import './Register.css';
//import axios from 'axios';
import {parseJwt} from "./jwt_util";
import apiClient from '../interceptor/axiosConfig';


function RegisterModal({ isOpen, onClose, onRegisterSuccess }) {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);  // 新增loading状态

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');  // 重置错误消息
        setLoading(true);  // 开始加载

        // 输出表单内容到控制台
        console.log("Registering with:", {
            username,
            email,
            password,
            confirmPassword
        });

        if (!emailRegex.test(email)) {
            setError('Invalid email format.');
            console.log("Error: Invalid email format.");  // 日志：邮箱格式不正确
            setLoading(false);  // 停止加载
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            console.log("Error: Passwords do not match.");  // 日志：密码不匹配
            setLoading(false);  // 停止加载
            return;
        }

        try {
            console.log("Sending registration request...");  // 日志：发送注册请求
            const response = await apiClient.post('/user/register', {
                username,
                email,
                password,
            });

            // 处理响应结果
            console.log("Registration response:", response.data);  // 输出服务器返回的数据
            if (response.data.status === "success") {
                onRegisterSuccess(response.data);  // 注册成功回调
                console.log("Registration successful:", response.data);  // 日志：注册成功

                const token = response.data.access_token;
                localStorage.setItem('jwtToken', token);
                console.log("token:{}", token)

                // 解析 JWT token 获取用户信息
                const decoded = parseJwt(token);
                console.log("Logged in as:", decoded.username);
                localStorage.setItem('username', decoded.username);

                onRegisterSuccess(decoded)

                onClose();  // 关闭模态框
            } else if (response.data.status === "error") {
                setError(response.data.message);  // 设置错误信息
                console.log("Error:", response.data.message);  // 日志：注册失败信息
                alert(response.data.message);  // 弹出错误提示
            }
        } catch (err) {
            console.log("Error: Registration failed.", err);  // 日志：请求失败
            alert(err);  // 弹出错误提示
        }

        setLoading(false);  // 请求完成，停止加载
        console.log("Loading state set to false.");  // 日志：加载状态结束
    };

    if (!isOpen) return null;

    return (
        <div className="register-modal">
            <div className="register-content">
                <h2>Register</h2>
                <form onSubmit={handleRegister}>
                    <div className="form-group">
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter your username"
                            disabled={loading}  // 加载时禁用输入框
                        />
                    </div>
                    <div className="form-group">
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            disabled={loading}  // 加载时禁用输入框
                        />
                    </div>
                    <div className="form-group">
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            disabled={loading}  // 加载时禁用输入框
                        />
                    </div>
                    <div className="form-group">
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="Confirm your password"
                            disabled={loading}  // 加载时禁用输入框
                        />
                    </div>
                    {error && <p className="error">{error}</p>}
                    <div className="button-group">
                        <button type="submit" className="register-btn" disabled={loading}>
                            {loading ? 'Registering...' : 'Register'}  {/* 显示加载状态 */}
                        </button>
                        <button type="button" className="cancel-btn" onClick={onClose} disabled={loading}>
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default RegisterModal;
