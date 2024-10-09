import React, { useContext, useEffect, useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, useNavigate, useLocation } from 'react-router-dom';
import LoginModal from './component/LoginModal';
import RegisterModal from './component/RegisterModal';
import Navbar from './component/Navbar';
import { parseJwt } from './component/jwt_util';
import Game from './component/Game';  // 假设你已经有 Game 组件
import {AuthContext, AuthProvider} from './context/AuthContext';

function App() {
    const { isModalOpen, setIsModalOpen, handleLoginSuccess, loggedInUser } = useContext(AuthContext);
    const [isRegisterOpen, setIsRegisterOpen] = useState(false);  // 添加控制 RegisterModal 的状态
    const navigate = useNavigate();
    const location = useLocation();

    // 检查JWT token是否存在，如果存在则设置登录状态
    useEffect(() => {
        const token = localStorage.getItem('jwtToken');
        const currentPath = location.pathname;

        if (token) {
            const userInfo = parseJwt(token);
            handleLoginSuccess(userInfo);
        } else if (currentPath === '/game') {
            // 如果用户未登录且试图访问受保护的 /game 页面时，重定向到首页
            navigate('/');
        }
    }, [navigate, location.pathname, handleLoginSuccess]);

    const handleGetStarted = () => {
        if (loggedInUser) {
            // 如果已经登录，跳转到游戏页面
            console.log("Already logged in, jump to /game")
            navigate('/game');
        } else {
            // 如果没有登录，显示登录模态框
            setIsModalOpen(true);
        }
    };

    return (
        <div className="App">
            {/* 导航栏 */}
            <Navbar
                loggedInUser={loggedInUser}
                onLoginClick={() => setIsModalOpen(true)}
                onRegisterClick={() => setIsRegisterOpen(true)}  // 点击注册时，打开 RegisterModal
            />

            {/* 路由配置 */}
            <Routes>
                {/* 首页 */}
                <Route
                    exact
                    path="/"
                    element={
                        <div>
                            <header className="App-header">
                                <div className="container">
                                    <h1>Welcome to Stream NZ!</h1>
                                    <h2>Beat AI Player to earn ETH!</h2>

                                    {/* Start Game按钮总是显示 */}
                                    <button className="start-btn" onClick={handleGetStarted}>Start Game</button>
                                </div>
                            </header>
                        </div>
                    }
                />

                {/* 游戏页面 */}
                <Route path="/game" element={<Game />} />
            </Routes>

            {/* 登录模态框 */}
            <LoginModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onLoginSuccess={handleLoginSuccess}
            />

            {/* 注册模态框 */}
            <RegisterModal
                isOpen={isRegisterOpen}  // 使用状态控制 RegisterModal 的打开和关闭
                onClose={() => setIsRegisterOpen(false)}  // 关闭注册模态框
            />
        </div>
    );
}

function AppWithRouter() {
    return (
        <AuthProvider>
            <Router>
                <App />
            </Router>
        </AuthProvider>
    );
}

export default AppWithRouter;
