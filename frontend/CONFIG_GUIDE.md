# 配置指南

## 统一配置说明

项目现在使用统一的配置文件 `src/config/config.js` 来管理所有的API端点。

## 配置文件结构

```javascript
// src/config/config.js
const config = {
  development: {
    API_BASE_URL: 'http://localhost:5050',
    SOCKET_URL: 'http://localhost:5050',
  },
  production: {
    API_BASE_URL: 'https://aiGame.streamnz.com',
    SOCKET_URL: 'https://aiGame.streamnz.com',
  }
};
```

## 环境自动切换

- **开发环境** (`npm start`): 自动使用 `localhost:5050`
- **生产环境** (`npm run build`): 自动使用 `https://aiGame.streamnz.com`

## 环境变量覆盖（可选）

如果需要自定义配置，可以创建环境变量文件：

### .env.development
```
REACT_APP_API_BASE_URL=http://localhost:5050
REACT_APP_SOCKET_URL=http://localhost:5050
```

### .env.production
```
REACT_APP_API_BASE_URL=https://aiGame.streamnz.com
REACT_APP_SOCKET_URL=https://aiGame.streamnz.com
```

## 使用方式

配置已经自动应用到：
- ✅ Socket.IO连接 (`Game.js`)
- ✅ HTTP API请求 (`axiosConfig.js`)

## 修改配置

只需要修改 `src/config/config.js` 文件中的对应环境配置即可，无需在多个文件中重复修改。 