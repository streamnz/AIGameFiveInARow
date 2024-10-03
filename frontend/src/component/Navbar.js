import React from 'react';
import './Navbar.css';  // 引入样式文件

function Navbar({ loggedInUser, onLoginClick, onRegisterClick, onLogoutClick }) {
  return (
    <div className="navbar">
      <div className="navbar-left">
        <h2>StreamNZ</h2>
      </div>

      <div className="navbar-right">
        {loggedInUser ? (
          // 如果用户已登录，显示 Welcome 和 Settings
          <div className="user-info">
            <span>Welcome, {loggedInUser.username}!</span>
            <button className="navbar-btn settings-btn">Settings</button>
            <button className="navbar-btn logout-btn" onClick={onLogoutClick}>Logout</button>
          </div>
        ) : (
          // 如果用户未登录，显示 Login 和 Register
          <div className="auth-buttons">
            <button className="navbar-btn login-btn" onClick={onLoginClick}>Login</button>
            <button className="navbar-btn register-btn" onClick={onRegisterClick}>Register</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Navbar;
