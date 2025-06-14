import math
from flask_socketio import emit, disconnect
import threading
from utils.jwt_util import get_decoded_token_from_request, decode_jwt_token
from ai.deepseek_ai import DeepSeekAI

# 15x15 棋盘尺寸
board_size = 15

# 用于存储所有用户对局状态的字典
games = {}
games_lock = threading.Lock()

# 初始化 OpenAI AI
deepseek_ai = DeepSeekAI()

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
                    "winner": None
                }
    except Exception as e:
        print(f"Connection error: {str(e)}")
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
            
            # 使用 OpenAI AI 获取第一步移动
            ai_x, ai_y = deepseek_ai.get_move(board, 'black')
            
            # 更新棋盘状态
            board[ai_x][ai_y] = 'black'
            games[session_id]['current_player'] = 'white'

            print(f"AI placed black piece at ({ai_x}, {ai_y}) for session ID: {session_id}")

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
                    print("AI is making its move...")
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

    print(f"AI is calculating its next move ({ai_player_color}) for session ID: {session_id}")

    board = games[session_id]['board']
    
    # 使用 OpenAI AI 获取下一步移动
    move_i, move_j = deepseek_ai.get_move(board, ai_player_color)

    # 更新棋盘状态
    board[move_i][move_j] = ai_player_color
    next_turn = 'black' if ai_player_color == 'white' else 'white'
    games[session_id]['current_player'] = next_turn

    print(f"AI placed {ai_player_color} piece at ({move_i}, {move_j}) for session ID: {session_id}")

    # 检查 AI 是否获胜
    if not check_and_emit_winner(session_id, move_i, move_j, ai_player_color):
        emit('updateBoard', {
            'board': games[session_id]['board'], 
            'next_turn': next_turn
        }, broadcast=True)

# 检查胜负条件
def check_winner(board, x, y, player):
    """检查指定玩家在指定位置是否获胜"""
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

        if count >= 5:
            print(f"{player} wins with {count} in a row!")
            return player

    return None

# 检查并发送获胜信息
def check_and_emit_winner(session_id, x, y, player):
    """检查是否有玩家获胜，如果有则发送获胜信息"""
    winner = check_winner(games[session_id]['board'], x, y, player)
    if winner:
        games[session_id]['status'] = 'ended'
        games[session_id]['winner'] = winner
        emit('gameOver', {'winner': winner}, broadcast=True)
        print(f"Game over! Winner: {winner} for session ID: {session_id}")
        return True
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
                    "winner": None
                }
                emit('updateBoard', {'board': games[session_id]['board']}, broadcast=True)
                print(f"Game reset for session ID: {session_id}")
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
