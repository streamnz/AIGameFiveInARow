import axios from 'axios';
import { AuthContext } from '../context/AuthContext';

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'https://aigame.streamnz.com', // 你的后端API基础URL
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

// 响应拦截器：捕获非200错误状态，弹出登录模态框和message信息
apiClient.interceptors.response.use(
  (response) => response,  // 成功请求的处理
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      // 处理401错误，清除token并显示登录模态框
      if (status === 401) {
        localStorage.removeItem('jwtToken');
        localStorage.removeItem('username');
        localStorage.removeItem('loggedInUser');

        if (AuthContext._currentValue) {
          AuthContext._currentValue.handle401Error();  // 调用显示LoginModal的函数
        }
      }

      // 处理非200状态，弹出后端返回的message
      if (status !== 200 && data.message) {
        alert(data.message);  // 弹出后端返回的message信息
      }
    } else {
      // 如果没有response，显示一个默认错误信息
      alert('An unexpected error occurred');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
