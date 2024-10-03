import React, { useState, useEffect } from 'react';
import './App.css';
import LoginModal from './component/LoginModal';
import Navbar from './component/Navbar';  // 引入 Navbar 组件

// 从 jwt_util.js 中导入 parseJwt 函数
import { parseJwt } from './component/jwt_util';  // 假设 jwt_util.js 在 component 文件夹下

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(null);

  // 打开模态框的函数
  const handleGetStarted = () => {
    setIsModalOpen(true);  // 点击按钮时打开模态框
  };

  // 关闭模态框的函数
  const handleCloseModal = () => {
    setIsModalOpen(false);  // 点击关闭按钮时关闭模态框
  };

   // 登录成功时，更新用户信息
  const handleLoginSuccess = (userInfo) => {
    setLoggedInUser(userInfo);  // 更新用户状态
  };

  // 使用 useEffect 钩子来检查 localStorage 中是否有 JWT token
  useEffect(() => {
    const token = localStorage.getItem('jwtToken');  // 从 localStorage 获取 token
    if (token) {
      const userInfo = parseJwt(token);  // 使用 parseJwt 解析 token
      console.log("useEffect.parseJwtToken.getUserInfo", userInfo);
      setLoggedInUser(userInfo);  // 设置用户信息
    }
  }, []);

  const handleLoginClick = () => {
    setIsModalOpen(true);  // 显示登录模态框
  };

  const handleRegisterClick = () => {
    alert('Register functionality is coming soon!');  // 注册功能
  };

  return (
    <div className="App">
      {/* 添加 Navbar 组件 */}
      <Navbar
        loggedInUser={loggedInUser}
        onLoginClick={handleLoginClick}
        onRegisterClick={handleRegisterClick}
      />

      <header className="App-header">
        <div className="container">
          <h1>Welcome to Stream NZ!</h1>
          <h2>Beat AI Player to earn ETH!</h2>

          {/* 点击按钮时触发模态框弹出 */}
          <button className="start-btn" onClick={handleGetStarted}>Start Game</button>
        </div>
      </header>

      {/* 模态框组件 */}
      <LoginModal isOpen={isModalOpen} onClose={handleCloseModal} onLoginSuccess={handleLoginSuccess} />
    </div>
  );
}

export default App;
