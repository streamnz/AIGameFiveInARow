import React, { useState, useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, useNavigate, useLocation } from 'react-router-dom';
import LoginModal from './component/LoginModal';
import RegisterModal from './component/RegisterModal';
import Navbar from './component/Navbar';
import { parseJwt } from './component/jwt_util';
import Game from './component/Game';  // 假设你已经有 Game 组件

function App() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
    const [loggedInUser, setLoggedInUser] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    // 检查JWT token是否存在，如果存在则设置登录状态
    useEffect(() => {
        const token = localStorage.getItem('jwtToken');
        const currentPath = location.pathname;

        if (token) {
            const userInfo = parseJwt(token);
            setLoggedInUser(userInfo);
        } else if (currentPath === '/game') {
            // 如果用户未登录且试图访问受保护的 /game 页面时，重定向到首页
            navigate('/');
        }
    }, [navigate, location.pathname]);  // 加入 location.pathname 来确保只在路径变化时触发

    const handleGetStarted = () => {
        if (loggedInUser) {
            // 如果已经登录，跳转到游戏页面
            navigate('/game');
        } else {
            // 如果没有登录，显示登录模态框
            setIsModalOpen(true);
        }
    };

    const handleLoginClick = () => {
        setIsModalOpen(true);  // 点击登录按钮，弹出登录模态框
    };

    const handleRegisterClick = () => {
        setIsRegisterModalOpen(true);  // 点击注册按钮，弹出注册模态框
    };

    const handleLoginSuccess = (userInfo) => {
        setLoggedInUser(userInfo);
        setIsModalOpen(false);  // 登录成功后关闭模态框
        navigate('/');  // 登录成功后回到首页，用户可以点击 Start Game
    };

    const handleLogoutSuccess = () => {
        setLoggedInUser(null);
        localStorage.removeItem('jwtToken');  // 清除JWT token
        if (location.pathname === '/game') {
            navigate('/');  // 如果用户在游戏页面时登出，跳回首页
        }
    };

    const handleRegisterSuccess = (userInfo) => {
        setLoggedInUser(userInfo);
        setIsRegisterModalOpen(false);  // 注册成功后关闭模态框
    };

    return (
        <div className="App">
            {/* 导航栏 */}
            <Navbar
                loggedInUser={loggedInUser}
                onLoginClick={handleLoginClick}
                onRegisterClick={handleRegisterClick}
                onLogoutSuccess={handleLogoutSuccess}
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
                isOpen={isRegisterModalOpen}
                onClose={() => setIsRegisterModalOpen(false)}
                onRegisterSuccess={handleRegisterSuccess}
            />
        </div>
    );
}

function AppWithRouter() {
    return (
        <Router>
            <App />
        </Router>
    );
}

export default AppWithRouter;
