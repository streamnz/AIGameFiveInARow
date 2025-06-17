import axios from 'axios';
import config from '../config/config';

// 创建axios实例
const apiClient = axios.create({
  baseURL: config.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true  // 允许跨域请求携带凭证
});

// 全局变量存储AuthContext，用于在拦截器中调用
let authContextRef = null;

// 设置AuthContext引用的函数
export const setAuthContext = (authContext) => {
  authContextRef = authContext;
};

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
    console.log('API Error:', error.response?.status, error.response?.data);
    
    if (error.response) {
      const { status, data } = error.response;

      // 处理401错误，清除token并显示登录模态框
      if (status === 401) {
        console.log('Token expired or invalid, clearing localStorage and showing login modal');
        
        // 清除所有认证相关的localStorage数据
        localStorage.removeItem('jwtToken');
        localStorage.removeItem('username');
        localStorage.removeItem('loggedInUser');

        // 触发登录模态框
        if (authContextRef && authContextRef.handle401Error) {
          authContextRef.handle401Error();
        } else {
          console.warn('AuthContext not available, manually triggering login modal');
          // 如果AuthContext不可用，直接操作DOM或使用其他方式
          window.dispatchEvent(new CustomEvent('tokenExpired'));
        }

        // 如果当前在受保护的页面，重定向到首页
        if (window.location.pathname === '/game' || window.location.pathname === '/settings') {
          window.location.href = '/';
        }
      }

      // 处理非200状态，弹出后端返回的message
      if (status !== 200 && data?.message) {
        alert(data.message);  // 弹出后端返回的message信息
      }
    } else {
      // 如果没有response，显示一个默认错误信息
      console.error('Network error or server unavailable');
      alert('Network error, please check your connection');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
