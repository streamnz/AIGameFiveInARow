import React, { useState } from 'react';
import axios from 'axios';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/login', {
        username: username,
        password: password,
      });

      const token = response.data.access_token;
      localStorage.setItem('token', token);  // 将token存储到localStorage中

      window.location.href = '/dashboard';  // 登录成功后跳转到受保护的页面
    } catch (error) {
      setError('用户名或密码错误');
    }
  };

  return (
    <div>
      <h2>登录</h2>
      <form onSubmit={handleLogin}>
        <div>
          <label>用户名:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>密码:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit">登录</button>
      </form>
    </div>
  );
}

export default Login;
