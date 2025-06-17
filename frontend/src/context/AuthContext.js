import React, { createContext, useState, useEffect, useCallback } from 'react';
import apiClient, { setAuthContext } from '../interceptor/axiosConfig';
import { parseJwt } from "../component/jwt_util";

// 创建上下文
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [loggedInUser, setLoggedInUser] = useState(null);

    // 处理401错误时显示登录模态框
    const handle401Error = useCallback(() => {
        console.log('handle401Error called, opening login modal');
        setLoggedInUser(null);
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

    // 检查token是否过期
    const checkTokenExpiry = useCallback(() => {
        const token = localStorage.getItem('jwtToken');
        if (token) {
            try {
                const decoded = parseJwt(token);
                const currentTime = Date.now() / 1000;
                
                if (decoded.exp < currentTime) {
                    console.log('Token has expired, clearing data and showing login modal');
                    handle401Error();
                }
            } catch (error) {
                console.error('Error parsing token:', error);
                handle401Error();
            }
        }
    }, [handle401Error]);

    // 使用 useEffect 加载存储在 localStorage 中的用户信息（例如 token）
    useEffect(() => {
        const storedUser = localStorage.getItem('loggedInUser');
        if (storedUser) {
            setLoggedInUser(JSON.parse(storedUser));
        }

        // 检查token是否过期
        checkTokenExpiry();

        // 设置定时器定期检查token过期
        const tokenCheckInterval = setInterval(checkTokenExpiry, 60000); // 每分钟检查一次

        // 注册AuthContext到axios拦截器
        const authContextMethods = {
            handle401Error,
            handleLoginSuccess,
            handleLogout,
            handleRegisterSuccess
        };
        setAuthContext(authContextMethods);

        // 监听自定义的token过期事件
        const handleTokenExpiredEvent = () => {
            console.log('Received tokenExpired event');
            handle401Error();
        };
        window.addEventListener('tokenExpired', handleTokenExpiredEvent);

        // 清理函数
        return () => {
            clearInterval(tokenCheckInterval);
            window.removeEventListener('tokenExpired', handleTokenExpiredEvent);
        };
    }, [handle401Error, handleLoginSuccess, handleLogout, handleRegisterSuccess, checkTokenExpiry]);

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
