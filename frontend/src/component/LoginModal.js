import React, { useState } from 'react';
import './LoginModal.css';
import axios from 'axios';

const LoginModal = ({ isOpen, onClose }) => {
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

    try {
      const response = await axios.post('/user/login', {
        username: username,
        password: password,
      });

      console.log(response)
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      console.log("token:{}",token)

      // 清除错误信息
      setError('');
      // 成功登录后关闭模态框
      onClose();
    } catch (error) {
      setError('User name or password wrong!');
    } finally {
      // 无论成功还是失败，最终都会取消 loading 状态
      setLoading(false);
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
          {error && <p style={{ color: 'red' }}>{error}</p>}
          {loading ? (  // 如果 loading 为 true，显示加载动画
            <div className="loading-spinner"></div>
          ) : (
            <button type="submit">Login</button>
          )}
        </form>
      </div>
    </div>
  );
};

export default LoginModal;
