import React, { useState } from 'react';
import './LoginModal.css';

const LoginModal = ({ isOpen, onClose }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // 正则表达式用于验证邮箱格式
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  const handleLogin = (e) => {
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

    // 登录逻辑
    console.log('Login attempted with', username, password);
    // 清除错误信息
    setError('');
    // 成功登录后关闭模态框
    onClose();
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
              placeholder="Enter your email"  // 添加灰色提示
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Password:</label>
            <input
              type="password"
              placeholder="Enter your password"  // 添加灰色提示
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  );
};

export default LoginModal;
