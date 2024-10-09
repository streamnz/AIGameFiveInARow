import React, { createContext, useState, useEffect } from 'react';
import apiClient from '../interceptor/axiosConfig';
import { parseJwt } from "../component/jwt_util";

// 创建上下文
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [loggedInUser, setLoggedInUser] = useState(null);

    // 使用 useEffect 加载存储在 localStorage 中的用户信息（例如 token）
    useEffect(() => {
        const storedUser = localStorage.getItem('loggedInUser');
        if (storedUser) {
            setLoggedInUser(JSON.parse(storedUser));
        }
    }, []);

    // 处理401错误时显示登录模态框
    const handle401Error = () => {
        setIsModalOpen(true);
    };

    // 登录成功时
    const handleLoginSuccess = (userInfo) => {
        setLoggedInUser(userInfo);
        localStorage.setItem('loggedInUser', JSON.stringify(userInfo));  // 存储登录信息到 localStorage
        setIsModalOpen(false);  // 关闭登录模态框
    };

    // 登出功能 (包含原始的 handleLogout 逻辑)
    const handleLogout = async () => {
        try {
            // 从 localStorage 获取 JWT token
            const token = localStorage.getItem('jwtToken');

            // 如果 token 不存在，直接清除用户名信息
            if (!token) {
                setIsModalOpen(true);  // 触发登录模态框
                return;
            }

            // 调用后端的登出接口，设置 Authorization 请求头
            await apiClient.post('/user/logout', {}, {
                headers: {
                    'Authorization': `Bearer ${token}`  // 在请求头中设置 token
                }
            });

            console.log("logout successfully!", parseJwt(token));

            // 清空 localStorage 中的用户信息
            localStorage.removeItem('jwtToken');
            localStorage.removeItem('username');
            localStorage.removeItem('loggedInUser');
            setLoggedInUser(null);  // 清除当前登录用户状态
        } catch (error) {
            console.error("Logout failed:", error);
        }
    };

    // 注册成功时
    const handleRegisterSuccess = (token) => {
        localStorage.setItem('jwtToken', token);
        // 解析 JWT token 获取用户信息
        const newUserInfo = parseJwt(token);
        setLoggedInUser(newUserInfo);
        localStorage.setItem('loggedInUser', JSON.stringify(newUserInfo));  // 注册成功后存储用户信息
        setIsModalOpen(false);  // 关闭模态框
    };

    return (
        <AuthContext.Provider value={{
            isModalOpen,
            setIsModalOpen,
            handle401Error,
            handleLoginSuccess,
            handleLogout,  // 通过 AuthContext 提供 handleLogout
            handleRegisterSuccess,
            loggedInUser
        }}>
            {children}
        </AuthContext.Provider>
    );
};
