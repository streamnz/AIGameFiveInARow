import React, { useState } from 'react';  // 引入useState钩子
import './App.css';  // 引入样式文件
import LoginModal from './component/LoginModal';  // 引入LoginModal组件

function App() {
  // 使用useState来控制模态框的显示状态
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 打开模态框的函数
  const handleGetStarted = () => {
    setIsModalOpen(true);  // 点击按钮时打开模态框
  };

  // 关闭模态框的函数
  const handleCloseModal = () => {
    setIsModalOpen(false);  // 点击关闭按钮时关闭模态框
  };

  return (
    <div className="App">
      <div className="container">
        <h1>StreamNZ - Ultimate Gaming Destination</h1>
        <h2>Beat AI Player to earn ETH!</h2>

        {/* 点击按钮时触发模态框弹出 */}
        <button className="start-btn" onClick={handleGetStarted}>Start Game</button>

        {/* 模态框组件 */}
        <LoginModal isOpen={isModalOpen} onClose={handleCloseModal} />
      </div>
    </div>
  );
}

export default App;
