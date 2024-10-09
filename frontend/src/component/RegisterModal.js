import React, { useState, useContext } from 'react';
import './Register.css';
import { parseJwt } from "./jwt_util";
import apiClient from '../interceptor/axiosConfig';
import { AuthContext } from '../context/AuthContext';

function RegisterModal({ isOpen, onClose }) {
    const { handleRegisterSuccess } = useContext(AuthContext);  // 从 AuthContext 获取状态管理函数
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

        if (!emailRegex.test(email)) {
            setError('Invalid email format.');
            setLoading(false);  // 停止加载
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            setLoading(false);  // 停止加载
            return;
        }

        try {
            const response = await apiClient.post('/user/register', {
                username,
                email,
                password,
            });

            if (response.data.status === "success") {
                const token = response.data.access_token;

                // 通过 AuthContext 更新注册成功后的状态
                handleRegisterSuccess(token);

                onClose();  // 关闭模态框
            } else if (response.data.status === "error") {
                setError(response.data.message);  // 设置错误信息
            }
        } catch (err) {
            setError('Registration failed.');
        }

        setLoading(false);  // 停止加载
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
