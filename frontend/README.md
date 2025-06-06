# CryptoChess - 加密货币五子棋游戏

这是一个基于 React 构建的现代化五子棋游戏，采用了 RabbitHole 风格的设计理念。玩家可以与AI对战并赢取ETH奖励。

## 🎨 设计特色

- **现代化深色主题**: 采用科技感十足的深色背景和渐变色彩
- **浮动装饰元素**: 页面包含动态浮动的游戏相关图标
- **响应式设计**: 支持桌面端、平板和手机端
- **毛玻璃效果**: 使用 backdrop-filter 实现现代化的毛玻璃效果
- **流畅动画**: 精心设计的hover效果和过渡动画

## 📁 项目结构

```
frontend/
├── src/
│   ├── component/
│   │   ├── LandingPage.js          # 新的首页组件
│   │   ├── LandingPage.css         # 首页样式文件
│   │   ├── Navbar.js               # 导航栏组件
│   │   ├── Navbar.css              # 导航栏样式
│   │   ├── Game.js                 # 游戏主组件
│   │   ├── LoginModal.js           # 登录模态框
│   │   └── RegisterModal.js        # 注册模态框
│   ├── context/
│   │   └── AuthContext.js          # 用户认证上下文
│   ├── App.js                      # 主应用组件
│   └── App.css                     # 全局样式
└── public/
```

## 🚀 新增功能

### 新首页组件 (LandingPage)
- **英雄区域**: 包含主标题、副标题和CTA按钮
- **游戏预览**: 展示五子棋棋盘预览
- **特性展示**: 三个主要功能卡片（AI对手、ETH奖励、实时对战）
- **玩法说明**: 三步式游戏流程说明

### 更新的导航栏
- **现代化设计**: 毛玻璃效果和渐变色品牌标志
- **响应式**: 适配移动端的简化布局
- **交互效果**: 精致的hover动画

### 样式亮点
- **渐变色**: 使用紫色到青色的现代渐变
- **动画效果**: 浮动元素和按钮hover效果
- **毛玻璃**: backdrop-filter实现的现代视觉效果
- **阴影**: 多层次的阴影效果增强深度感

## 🛠️ 运行项目

```bash
# 安装依赖
npm install

# 启动开发服务器
npm start

# 构建生产版本
npm run build
```

## 🎯 主要改进

1. **视觉升级**: 从传统设计升级为现代科技风格
2. **用户体验**: 更直观的游戏介绍和操作流程
3. **品牌形象**: 统一的视觉语言和色彩体系
4. **性能优化**: 优化的CSS和组件结构

## 🎮 游戏功能

- 与AI对战五子棋
- 用户注册/登录系统
- ETH奖励机制
- 实时游戏状态更新
- 胜负统计

## 🔧 技术栈

- **前端**: React 18
- **样式**: CSS3 (Grid, Flexbox, Backdrop-filter)
- **动画**: CSS Transitions & Keyframes
- **状态管理**: React Context API
- **路由**: React Router
- **构建工具**: Create React App

## 📱 响应式设计

- **桌面端**: 完整的功能和视觉效果
- **平板端**: 优化的布局和间距
- **手机端**: 简化的导航和紧凑的布局

## 🎨 设计灵感

本项目的设计灵感来源于 RabbitHole 等现代加密货币应用的设计理念，融合了：
- Web3 应用的视觉语言
- 现代化的卡片式布局
- 科技感的深色主题
- 流畅的交互动画

---

现在你的五子棋游戏拥有了一个现代化、专业的首页！🎉

# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
