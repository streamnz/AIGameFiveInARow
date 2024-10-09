import React, { createContext, useState } from 'react';

// 创建上下文
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [loggedInUser, setLoggedInUser] = useState(null);

    // 处理401错误时显示登录模态框
    const handle401Error = () => {
        setIsModalOpen(true);
    };

    // 登录成功时
    const handleLoginSuccess = (userInfo) => {
        setLoggedInUser(userInfo);
        setIsModalOpen(false);  // 关闭模态框
    };

    return (
        <AuthContext.Provider value={{ isModalOpen, setIsModalOpen, handle401Error, handleLoginSuccess, loggedInUser }}>
            {children}
        </AuthContext.Provider>
    );
};
