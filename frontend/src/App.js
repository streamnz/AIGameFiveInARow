import React from 'react';
import './App.css'; // 引入样式文件

function App() {
  return (
    <div className="App">
      <div className="container">
        <h1>StreamNZ - Ultimate Gaming Destination</h1>
        <h2>Beat AI Player to earn ETH!</h2>

        <button className="start-btn">Start Game</button>

        {/* 模态框部分 */}
        <div className="login-modal" id="loginModal">
          <div className="login-modal-content">
            <div className="close-btn">&times;</div>
            <h2>Please Login</h2>
            <input type="text" placeholder="Username" />
            <input type="password" placeholder="Password" />
            <button>Login</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
