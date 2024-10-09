import React from 'react';
import './Navbar.css';
//import axios from "axios";
import {parseJwt} from "./jwt_util";  // 引入样式文件
import apiClient from '../interceptor/axiosConfig';


function Navbar({loggedInUser, onLoginClick, onRegisterClick, onLogoutSuccess}) {

    // 登出函数
    const handleLogout = async () => {
        try {
            // 从 localStorage 获取 JWT token
            const token = localStorage.getItem('jwtToken');

            // 如果 token 不存在，则直接返回错误
            if (!token) {
                console.error("No token found, user might not be logged in.");
                return;
            }

            // 调用后端的登出接口，设置 Authorization 请求头
            await apiClient.post('/user/logout', {}, {
                headers: {
                    'Authorization': `Bearer ${token}`  // 在请求头中设置 token
                }
            });

            console.log("logout successfully!",parseJwt(token))

            // 清空 localStorage
            localStorage.removeItem('jwtToken');

            // 调用父组件传入的登出成功函数，更新UI状态
            onLogoutSuccess();

        } catch (error) {
            console.error("Logout failed:", error);
        }
    };
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
                        <button className="navbar-btn logout-btn" onClick={handleLogout}>Logout</button>
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
