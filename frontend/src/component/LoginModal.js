import React, {useState} from 'react';
import './LoginModal.css';
import axios from 'axios';

import { parseJwt } from './jwt_util';


const LoginModal = ({isOpen, onClose,onLoginSuccess}) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);  // 引入 loading 状态

    // 正则表达式用于验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const handleLogin = async (e) => {
        e.preventDefault();

        // 校验邮箱格式
        if (!emailRegex.test(username)) {
            setError('Invalid email format');
            return;
        }

        // 校验密码是否为空
        if (!password) {
            setError('Password cannot be empty');
            return;
        }

        // 设置 loading 状态为 true，表示请求正在进行
        setLoading(true);
        console.log(" set loading is true")

        try {
            const response = await axios.post('/user/login', {
                username: username,
                password: password,
            });

            console.log(response)
            const token = response.data.access_token;
            localStorage.setItem('jwtToken', token);
            console.log("token:{}", token)

            // 解析 JWT token 获取用户信息
            const decoded = parseJwt(token);
            console.log("Logged in as:", decoded.username);
            localStorage.setItem('username', decoded.username);

            onLoginSuccess(decoded)

            // 清除错误信息
            setError('');
            // 成功登录后关闭模态框
            onClose();
        } catch (error) {
            setError('User name or password wrong!');
        } finally {
            // 无论成功还是失败，最终都会取消 loading 状态
            setLoading(false);
            console.log(" set loading is false")
        }
    };

    if (!isOpen) return null; // 如果模态框未打开，则不渲染

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <button className="close-btn" onClick={onClose}>×</button>
                <h3>Login</h3>
                <form onSubmit={handleLogin}>
                    <div>
                        <label>Username (Email):</label>
                        <input
                            type="text"
                            placeholder="Enter your email"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <label>Password:</label>
                        <input
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    {error && <p style={{color: 'red'}}>{error}</p>}
                    {loading ? (
                       <div className="loading-spinner-login"></div>
                    ) : (
                        <button type="submit">Login</button>
                    )}
                </form>
            </div>
        </div>
    );
};

export default LoginModal;
