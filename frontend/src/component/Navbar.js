import React, { useContext } from 'react';
import './Navbar.css';
import { AuthContext } from '../context/AuthContext';  // 引入 AuthContext
import { useNavigate } from 'react-router-dom';

function Navbar({ onLoginClick, onRegisterClick }) {
    const { loggedInUser, handleLogout } = useContext(AuthContext);  // 从 AuthContext 获取用户信息和登出函数
    const navigate = useNavigate();

    // 封装登出并跳转首页
    const handleLogoutAndRedirect = async () => {
        await handleLogout();
        navigate('/');
    };

    // 点击标题回到首页
    const handleTitleClick = () => {
        navigate('/');
    };

    return (
        <div className="navbar">
            <div className="navbar-left">
                <h2 className="navbar-title" onClick={handleTitleClick}>CryptoChess</h2>
            </div>

            <div className="navbar-right">
                {loggedInUser ? (
                    // 如果用户已登录，显示 Welcome 和 Settings
                    <div className="user-info">
                        <span>Kia Ora, {loggedInUser.username}!</span>
                        <button className="navbar-btn about-btn" onClick={() => navigate('/about')}>About</button>
                        <button className="navbar-btn settings-btn" onClick={() => navigate('/settings')}>Settings</button>
                        <button className="navbar-btn logout-btn" onClick={handleLogoutAndRedirect}>Logout</button>
                    </div>
                ) : (
                    // 如果用户未登录，显示 Login 和 Register
                    <div className="auth-buttons">
                        <button className="navbar-btn about-btn" onClick={() => navigate('/about')}>About</button>
                        <button className="navbar-btn navbar-login-btn" onClick={onLoginClick}>Login</button>
                        <button className="navbar-btn navbar-register-btn" onClick={onRegisterClick}>Register</button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Navbar;
