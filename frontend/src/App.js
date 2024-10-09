import React, { useState, useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';  // 使用useNavigate代替useHistory
import LoginModal from './component/LoginModal';
import RegisterModal from './component/RegisterModal';
import Navbar from './component/Navbar';
import { parseJwt } from './component/jwt_util';
import Game from './component/Game';  // 假设你已经有 Game 组件

function App() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [loggedInUser, setLoggedInUser] = useState(null);
    const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
    const navigate = useNavigate();  // 使用useNavigate进行页面跳转

    useEffect(() => {
        const token = localStorage.getItem('jwtToken');
        if (token) {
            const userInfo = parseJwt(token);
            setLoggedInUser(userInfo);
        }
    }, []);

    const handleGetStarted = () => {
        if (loggedInUser) {
            // 如果已经登录，跳转到游戏页面
            navigate('/game');
        } else {
            // 如果没有登录，显示登录模态框
            setIsModalOpen(true);
        }
    };

    const handleLoginSuccess = (userInfo) => {
        setLoggedInUser(userInfo);
        setIsModalOpen(false);  // 登录成功后关闭模态框
        navigate('/game');  // 登录后直接跳转到游戏页面
    };

    const handleRegisterClick = () => {
        setIsRegisterModalOpen(true);
    };

    const handleLogoutSuccess = () => {
        setLoggedInUser(null);
        setIsModalOpen(false);
    };

    const handleRegisterSuccess = (userInfo) => {
        setLoggedInUser(userInfo);
    };

    return (
        <div className="App">
            <Navbar
                loggedInUser={loggedInUser}
                onLoginClick={() => setIsModalOpen(true)}
                onRegisterClick={handleRegisterClick}
                onLogoutSuccess={handleLogoutSuccess}
            />

            <header className="App-header">
                <div className="container">
                    <h1>Welcome to Stream NZ!</h1>
                    <h2>Beat AI Player to earn ETH!</h2>

                    {/* 点击按钮时触发模态框弹出或跳转到游戏页面 */}
                    <button className="start-btn" onClick={handleGetStarted}>Start Game</button>
                </div>
            </header>

            {/* 路由配置 */}
            <Routes>
                <Route exact path="/" element={<div>Home</div>} />
                <Route path="/game" element={<Game />} />
            </Routes>

            {/* 登录模态框 */}
            <LoginModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onLoginSuccess={handleLoginSuccess} />

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
