import React, {useContext, useEffect, useState} from 'react';
import './App.css';
import {BrowserRouter as Router, Route, Routes, useNavigate, useLocation} from 'react-router-dom';
import LoginModal from './component/LoginModal';
import RegisterModal from './component/RegisterModal';
import Navbar from './component/Navbar';
import LandingPage from './component/LandingPage';
import Settings from './component/Settings';
import About from './component/About';
import Resume from './component/Resume';
import {parseJwt} from './component/jwt_util';
import Game from './component/Game';
import {AuthContext, AuthProvider} from './context/AuthContext';

function App() {
    const {isModalOpen, setIsModalOpen, handleLoginSuccess, loggedInUser} = useContext(AuthContext);
    const [isRegisterOpen, setIsRegisterOpen] = useState(false); // 控制 RegisterModal 状态
    const navigate = useNavigate();
    const location = useLocation();

    // 检查JWT token是否存在，如果存在则设置登录状态
    useEffect(() => {
        const token = localStorage.getItem('jwtToken');
        const currentPath = location.pathname;
        const userInfo = parseJwt(token);

        if (token && userInfo) {
            handleLoginSuccess(userInfo);
        } else if (currentPath === '/game') {
            // 如果用户未登录且试图访问受保护的 /game 页面时，重定向到首页
            navigate('/');
        }
    }, [location.pathname, navigate]);

    const handleGetStarted = () => {
        if (loggedInUser) {
            console.log("Already logged in, jump to /game");
            navigate('/game');
        } else {
            setIsModalOpen(true); // 如果没有登录，显示登录模态框
        }
    };

    return (
        <div className="App">
            {/* 导航栏 */}
            <Navbar
                loggedInUser={loggedInUser}
                onLoginClick={() => setIsModalOpen(true)}
                onRegisterClick={() => setIsRegisterOpen(true)} // 点击注册时，打开 RegisterModal
            />

            {/* 路由配置 */}
            <Routes>
                {/* 首页 */}
                <Route
                    exact
                    path="/"
                    element={
                        <LandingPage 
                            onGetStarted={handleGetStarted}
                            loggedInUser={loggedInUser}
                        />
                    }
                />

                {/* 游戏页面 */}
                <Route path="/game" element={<Game/>}/>
                
                {/* 设置页面 */}
                <Route path="/settings" element={<Settings/>}/>
                
                {/* About页面 */}
                <Route path="/about" element={<About/>}/>
                
                {/* Resume页面 */}
                <Route path="/resume" element={<Resume/>}/>
            </Routes>

            {/* 登录模态框 */}
            <LoginModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onLoginSuccess={handleLoginSuccess}
            />

            {/* 注册模态框 */}
            <RegisterModal
                isOpen={isRegisterOpen}
                onClose={() => setIsRegisterOpen(false)} // 关闭注册模态框
            />
        </div>
    );
}

function AppWithRouter() {
    return (
        <AuthProvider>
            <Router>
                <App/>
            </Router>
        </AuthProvider>
    );
}

export default AppWithRouter;
