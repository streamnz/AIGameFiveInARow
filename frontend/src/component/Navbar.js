// src/component/Navbar.js
import React from 'react';
import './Navbar.css';  // 引入样式文件

function Navbar({ loggedInUser, onLoginClick, onRegisterClick }) {
  return (
    <div className="navbar">
      <div className="navbar-left">
        <h2>StreamNZ</h2>
      </div>

      <div className="navbar-right">
        {loggedInUser ? (
          // 如果用户已登录，显示用户名和设置
          <div className="user-info">
            <span>Welcome, {loggedInUser.username}!</span>
            <button className="settings-btn">Settings</button>
          </div>
        ) : (
          // 如果用户未登录，显示 Login 和 Register
          <div className="auth-buttons">
            <button className="login-btn" onClick={onLoginClick}>Login</button>
            <button className="register-btn" onClick={onRegisterClick}>Register</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Navbar;
