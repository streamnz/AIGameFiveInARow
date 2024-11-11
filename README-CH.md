# 五子棋AI对战系统

## 项目简介
这是一个基于AlphaZero算法的五子棋AI对战系统，采用前后端分离架构，集成了用户管理、AI对战、排行榜等功能。

## 技术栈
### 前端
- React
- Socket.IO-client
- Axios
- React Router

### 后端
- Python Flask
- MySQL
- WebSocket
- JWT认证

### AI模型
- PyTorch
- AlphaZero算法
- MCTS（蒙特卡洛树搜索）

## 主要功能
1. **用户系统**
   - 用户注册/登录
   - JWT token认证
   - 用户积分排行榜

2. **游戏功能**
   - 人机对战
   - 实时对局
   - 棋局状态保存
   - 胜负判定

3. **AI系统**
   - 基于AlphaZero的AI模型
   - 15x15棋盘支持
   - 可训练和优化的AI模型

## 项目结构 
````
FiveChessWithAI/
├── ai/
│   ├── game.py                  # Defines Board and Game classes for Gomoku
│   ├── human_play.py            # Implements human vs AI gameplay
│   ├── mcts_alphaZero.py        # Monte Carlo Tree Search for AlphaZero
│   ├── policy_value_net_pytorch.py # PyTorch implementation of policy-value network
│   ├── train.py                 # Training pipeline for AlphaZero
│   └── README.md                # Documentation for AI implementation
├── app.py                       # Flask application main entry point
├── config.py                    # Application configuration
├── controller/
│   ├── game_controller.py       # Handles game-related routes and logic
│   └── user_controller.py       # Handles user authentication and leaderboard
├── dao/
│   ├── game_dao.py              # Database access for game state
│   └── user_dao.py              # Database access for user management
├── model/
│   └── user.py                  # User model for authentication
├── service/
│   ├── game_service.py          # Business logic for the game
│   └── user_service.py          # Logic for managing users and authentication
├── source/
│   ├── AI.py                    # AI logic (Minimax with Alpha-Beta pruning)
│   ├── gomoku.py                # Game state management
│   └── utils.py                 # Helper functions for the game
├── static/                      # Static files (CSS, images, JavaScript)
├── templates/                   # HTML templates
├── utils/
│   ├── config.ini               # Configuration file
│   └── jwt_util.py              # JWT utility functions
├── websocket/
│   └── MyWebsocket.py           # WebSocket implementation for real-time gameplay
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
````
## 运行说明
### 后端启动
bash 
# 安装依赖 
pip install -r requirements.txt 
 
# 启动Flask服务 
python app.py
### 前端启动
bash 
cd frontend 
npm install 
npm start
## 配置说明
- 数据库配置在`config.py`中设置
- AI模型参数在`ai/train.py`中配置
- 前端API配置在`frontend/src/interceptor/axiosConfig.js`中设置

## 开发团队
- 开发者：Hao Cheng
- 许可证：MIT

## 注意事项
1. 确保Python版本 >= 3.7
2. 需要配置MySQL数据库
3. AI训练需要GPU支持（可选）
4. 确保前后端端口配置正确

## 未来计划
1. 增加多人对战功能
2. 优化AI模型性能
3. 添加对局回放功能
4. 引入难度等级设置