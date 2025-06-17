// 统一的API配置
const config = {
  // 开发环境配置
  development: {
    API_BASE_URL: '',  // 使用相对路径，让代理处理
    SOCKET_URL: 'http://localhost:5050',  // WebSocket 仍然需要完整路径
    IS_PRODUCTION: false
  },
  // 生产环境配置
  production: {
    API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'https://www.streamnz.com/api',
    SOCKET_URL: process.env.REACT_APP_SOCKET_URL || 'https://streamnz-api.streamnz.com',
    IS_PRODUCTION: true
  }
};

// 根据环境变量或默认使用开发环境
const environment = process.env.NODE_ENV || 'development';
const currentConfig = config[environment];

// 添加一些实用方法
currentConfig.isDevelopment = () => environment === 'development';
currentConfig.isProduction = () => environment === 'production';

console.log(`🌍 当前环境: ${environment}`);
console.log(`🔗 API地址: ${currentConfig.API_BASE_URL || '使用代理'}`);
console.log(`🔌 Socket地址: ${currentConfig.SOCKET_URL}`);

export default currentConfig; 