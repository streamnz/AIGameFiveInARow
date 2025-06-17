import math
from flask_socketio import emit, disconnect
import threading
from utils.jwt_util import get_decoded_token_from_request, decode_jwt_token
from ai.deepseek_ai import DeepSeekAI
from ai.llama3_ai import Llama3AI
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 15x15 棋盘尺寸
board_size = 15

# 用于存储所有用户对局状态的字典
games = {}
games_lock = threading.Lock()

# 初始化 AI 模型
deepseek_ai = DeepSeekAI()
llama3_ai = Llama3AI()

# AI 模型选择 - 从 .env 文件或环境变量中读取
AI_MODEL = os.getenv('AI_MODEL', 'deepseek')  # 默认使用 deepseek，可选 'llama3'

def get_ai_instance():
    """根据配置返回对应的 AI 实例"""
    if AI_MODEL.lower() == 'llama3':
        print("使用本地 Llama3 AI 模型")
        return llama3_ai
    else:
        print("使用 DeepSeek AI 模型")
        return deepseek_ai

# 客户端连接时的处理逻辑
def handle_connect():
    try:
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')

        with games_lock:
            print(f"Client connected with session ID: {session_id}")
            if session_id not in games:
                games[session_id] = {
                    "board": [['' for _ in range(board_size)] for _ in range(board_size)],
                    "current_player": "black",
                    "status": "ongoing",
                    "winner": None,
                    "ai_model": AI_MODEL  # 记录使用的 AI 模型
                }
    except Exception as e:
        print(f"Connection error: {str(e)}")
        if "expired" in str(e).lower():
            print("Token has expired, disconnecting client")
            emit('error', {'message': 'Token has expired, please login again'})
        else:
            print(f"Invalid token or other error: {str(e)}")
            emit('error', {'message': 'Authentication failed'})
        disconnect()

# 客户端断开连接时的处理逻辑
def handle_disconnect():
    try:
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')

        with games_lock:
            if session_id in games:
                print(f"Removing game for session ID: {session_id}")
                del games[session_id]
    except Exception as e:
        print(f"Disconnect error: {str(e)}")
    finally:
        print("Client disconnected")

# 处理 AI 先手的情况
def handle_ai_first_move():
    try:
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')

        with games_lock:
            if session_id not in games:
                print(f"No game found for session ID: {session_id}")
                return

            print(f"AI starts first move (black) for session ID: {session_id}")

            board = games[session_id]['board']
            
            # 使用选定的 AI 获取第一步移动
            ai_instance = get_ai_instance()
            ai_x, ai_y = ai_instance.get_move(board, 'black')
            
            # 更新棋盘状态
            board[ai_x][ai_y] = 'black'
            games[session_id]['current_player'] = 'white'

            print(f"AI ({AI_MODEL}) placed black piece at ({ai_x}, {ai_y}) for session ID: {session_id}")

            # 发送更新给客户端
            emit('updateBoard', {
                'board': games[session_id]['board'], 
                'next_turn': 'white'
            }, broadcast=True)

    except Exception as e:
        print(f"Error during AI first move: {str(e)}")
        disconnect()

# 处理玩家的走子动作
def handle_player_move(data):
    try:
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')

        with games_lock:
            if session_id not in games:
                print(f"No game found for session ID: {session_id}")
                return

            x, y = data['x'], data['y']
            player = data['player']

            print(f"Player {player} placed piece at ({x}, {y}) for session ID: {session_id}")

            game = games[session_id]
            board = game['board']

            # 验证移动有效性
            if board[x][y] == '':
                board[x][y] = player
                game['current_player'] = 'white' if game['current_player'] == 'black' else 'black'

                # 检查玩家是否获胜
                if not check_and_emit_winner(session_id, x, y, player):
                    print(f"AI ({AI_MODEL}) is making its move...")
                    # AI 响应玩家移动
                    ai_move(session_id, game['current_player'])
            else:
                print(f"Invalid move: Position ({x}, {y}) is already occupied for session ID: {session_id}")
                
    except Exception as e:
        print(f"Error during player move: {str(e)}")
        disconnect()

# AI 下棋逻辑
def ai_move(session_id, ai_player_color):
    if session_id not in games:
        print(f"No game found for session ID: {session_id}")
        return

    print(f"AI ({AI_MODEL}) is calculating its next move ({ai_player_color}) for session ID: {session_id}")

    board = games[session_id]['board']
    
    # 使用选定的 AI 获取下一步移动
    ai_instance = get_ai_instance()
    move_i, move_j = ai_instance.get_move(board, ai_player_color)

    # 更新棋盘状态
    board[move_i][move_j] = ai_player_color
    next_turn = 'black' if ai_player_color == 'white' else 'white'
    games[session_id]['current_player'] = next_turn

    print(f"AI ({AI_MODEL}) placed {ai_player_color} piece at ({move_i}, {move_j}) for session ID: {session_id}")

    # 检查 AI 是否获胜
    if not check_and_emit_winner(session_id, move_i, move_j, ai_player_color):
        emit('updateBoard', {
            'board': games[session_id]['board'], 
            'next_turn': next_turn
        }, broadcast=True)

# 处理切换 AI 模型
def handle_switch_ai_model(data):
    """处理切换 AI 模型的请求"""
    try:
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')
        
        new_model = data.get('model', 'deepseek').lower()
        if new_model not in ['deepseek', 'llama3']:
            print(f"Invalid AI model: {new_model}")
            return
        
        global AI_MODEL
        AI_MODEL = new_model
        
        with games_lock:
            if session_id in games:
                games[session_id]['ai_model'] = AI_MODEL
        
        print(f"AI model switched to: {AI_MODEL} for session ID: {session_id}")
        emit('aiModelChanged', {'model': AI_MODEL}, broadcast=True)
        
    except Exception as e:
        print(f"Error switching AI model: {str(e)}")

# 检查胜负条件
def check_winner(board, x, y, player):
    """检查指定玩家在指定位置是否获胜"""
    print(f"=== 检查获胜者 ===")
    print(f"检查位置: ({x}, {y}), 玩家: '{player}' (type: {type(player)})")
    print(f"该位置的实际值: '{board[x][y]}' (type: {type(board[x][y])})")
    
    # 打印棋盘周围区域用于调试
    print("棋盘周围区域:")
    for i in range(max(0, x-2), min(board_size, x+3)):
        row_str = ""
        for j in range(max(0, y-2), min(board_size, y+3)):
            if i == x and j == y:
                row_str += f"[{board[i][j] if board[i][j] else '.'}]"
            else:
                row_str += f" {board[i][j] if board[i][j] else '.'} "
        print(f"行{i}: {row_str}")
    
    # 确保player参数不为空
    if not player or player == '':
        print(f"警告: player参数为空或空字符串")
        return None
    
    # 确保指定位置确实是该玩家的棋子
    if board[x][y] != player:
        print(f"警告: 位置({x}, {y})的棋子'{board[x][y]}'与玩家'{player}'不匹配")
        print(f"棋盘该位置值的repr: {repr(board[x][y])}")
        print(f"玩家参数的repr: {repr(player)}")
        return None
    
    directions = [
        (0, 1),   # 水平方向
        (1, 0),   # 垂直方向
        (1, 1),   # 主对角线
        (1, -1)   # 副对角线
    ]

    for dx, dy in directions:
        count = 1
        
        # 向一个方向计数
        i, j = x + dx, y + dy
        while 0 <= i < board_size and 0 <= j < board_size and board[i][j] == player:
            count += 1
            i += dx
            j += dy

        # 向相反方向计数
        i, j = x - dx, y - dy
        while 0 <= i < board_size and 0 <= j < board_size and board[i][j] == player:
            count += 1
            i -= dx
            j -= dy

        print(f"方向({dx}, {dy}): 连子数 = {count}")
        
        if count >= 5:
            print(f"找到获胜: {player} 在方向({dx}, {dy})有 {count} 连子!")
            return player

    print(f"未找到获胜条件")
    return None

# 检查并发送获胜信息
def check_and_emit_winner(session_id, x, y, player):
    """检查是否有玩家获胜，如果有则发送获胜信息"""
    print(f"=== 检查并发送获胜信息 ===")
    print(f"会话ID: {session_id}, 位置: ({x}, {y}), 玩家: '{player}'")
    
    winner = check_winner(games[session_id]['board'], x, y, player)
    print(f"检查结果: winner = '{winner}' (type: {type(winner)})")
    
    if winner and winner != '':
        games[session_id]['status'] = 'ended'
        games[session_id]['winner'] = winner
        
        print(f"发送gameOver事件: winner = '{winner}' (type: {type(winner)}, repr: {repr(winner)})")
        game_over_data = {'winner': winner}
        print(f"gameOver数据: {game_over_data}")
        emit('gameOver', game_over_data, broadcast=True)
        print(f"Game over! Winner: {winner} for session ID: {session_id}")
        return True
    
    print(f"游戏继续，没有获胜者")
    return False

# 重置游戏
def handle_reset_game():
    try:
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')

        with games_lock:
            if session_id in games:
                games[session_id] = {
                    "board": [['' for _ in range(board_size)] for _ in range(board_size)],
                    "current_player": "black",
                    "status": "ongoing",
                    "winner": None,
                    "ai_model": AI_MODEL  # 保持当前 AI 模型设置
                }
                emit('updateBoard', {'board': games[session_id]['board']}, broadcast=True)
                print(f"Game reset for session ID: {session_id} with AI model: {AI_MODEL}")
            else:
                print(f"No game found to reset for session ID: {session_id}")
                
    except Exception as e:
        print(f"Error during game reset: {str(e)}")

# 处理用户登出
def handle_logout():
    try:
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')

        with games_lock:
            if session_id in games:
                del games[session_id]
                print(f"Game data cleared for session ID: {session_id}")
                
    except Exception as e:
        print(f"Error during logout: {str(e)}")
