import axios from 'axios';
import { AuthContext } from '../context/AuthContext';

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:5000', // 你的后端API基础URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：判断是否需要token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwtToken');

  // 如果请求的URL路径不是以 'base' 开头，则需要添加token
  if (!config.url.startsWith('/base') && token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
}, (error) => {
  return Promise.reject(error);
});

// 响应拦截器：捕获401错误，清除token并弹出登录模态框
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // 清除localStorage中的token
      localStorage.removeItem('jwtToken');

      // 显示LoginModal（通过AuthContext）
      if (AuthContext._currentValue) {
        AuthContext._currentValue.handle401Error();  // 调用显示LoginModal的函数
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
