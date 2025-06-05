import React, { createContext, useState, useEffect, useCallback } from 'react';
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
    }, []); // 添加空依赖数组，只在组件挂载时执行一次

    // 处理401错误时显示登录模态框
    const handle401Error = useCallback(() => {
        setIsModalOpen(true);
    }, []);

    // 登录成功时
    const handleLoginSuccess = useCallback((userInfo) => {
        setLoggedInUser(userInfo);
        localStorage.setItem('loggedInUser', JSON.stringify(userInfo));  // 存储登录信息到 localStorage
        setIsModalOpen(false);  // 关闭登录模态框
    }, []);

    // 登出功能
    const handleLogout = useCallback(async () => {
        try {
            const token = localStorage.getItem('jwtToken');
            if (!token) {
                setIsModalOpen(true);
                return;
            }

            setLoggedInUser(null);
            localStorage.removeItem('jwtToken');
            localStorage.removeItem('username');
            localStorage.removeItem('loggedInUser');

            await apiClient.post('/user/logout', {}, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            console.log("logout successfully!", parseJwt(token));
        } catch (error) {
            console.error("Logout failed:", error);
        }
    }, []);

    // 注册成功时
    const handleRegisterSuccess = useCallback((token) => {
        localStorage.setItem('jwtToken', token);
        const newUserInfo = parseJwt(token);
        setLoggedInUser(newUserInfo);
        localStorage.setItem('loggedInUser', JSON.stringify(newUserInfo));
        setIsModalOpen(false);
    }, []);

    return (
        <AuthContext.Provider value={{
            isModalOpen,
            setIsModalOpen,
            handle401Error,
            handleLoginSuccess,
            handleLogout,
            handleRegisterSuccess,
            loggedInUser
        }}>
            {children}
        </AuthContext.Provider>
    );
};
