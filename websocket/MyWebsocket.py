import math

from flask_socketio import emit, disconnect
from ai.human_play import PolicyValueNet
from ai.mcts_alphaZero import MCTSPlayer
from ai.game import Board
import torch
import threading

from source.AI import GomokuAI  # 导入 GomokuAI 类
from utils.jwt_util import get_decoded_token_from_request, decode_jwt_token

# 15x15 棋盘尺寸
board_size = 15

# 设置AI模型的路径
model_file = './ai/current_policy_15_15_5.model2'
use_gpu = torch.cuda.is_available()  # 检查是否有 GPU

# 初始化 AI 使用 PolicyValueNet 和 MCTSPlayer
policy_value_net = PolicyValueNet(board_size, board_size, model_file=model_file, use_gpu=use_gpu)
ai_player = MCTSPlayer(policy_value_net.policy_value_fn, c_puct=5, n_playout=400)

# 用于存储所有用户对局状态的字典
# 增加线程锁以保证线程安全
games = {}
games_lock = threading.Lock()

ai_instance = GomokuAI()

ai_source = 'source'


# 客户端连接时的处理逻辑
def handle_connect():
    try:
        # 使用 jwt_util 从请求中解码 token
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')  # 或者其他字段

        with games_lock:
            print(f"Client connected with session ID: {session_id}")
            if session_id not in games:
                # 初始化游戏状态
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
        session_id = decoded_token.get('sub')

        with games_lock:
            if session_id in games:
                print(f"Removing game for session ID: {session_id}")
                del games[session_id]  # 清理对局状态

    except Exception as e:
        print(f"Disconnect error: {str(e)}")
    finally:
        print("Client disconnected")


# 处理客户端选择白棋的情况，AI 先下第一步
def handle_ai_first_move():
    try:
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')

        with games_lock:
            if session_id not in games:
                print(f"No game found for session ID: {session_id}")
                return

            print(f"AI starts first move (black) for session ID: {session_id}")

            # 初始化游戏棋盘
            board = games[session_id]['board']
            game_board = _initialize_game_board(board)

            if ai_source == 'source':
                # 使用 GomokuAI 模型执行第一步
                ai_instance.firstMove()  # AI 默认在中心位置(7,7)下第一步
                ai_x, ai_y = ai_instance.currentI, ai_instance.currentJ
                board[ai_x][ai_y] = 'black'  # AI 落下黑子
                ai_instance.boardMap = _convert_board_to_source_format(board)
            else:
                # 使用 AlphaZero AI 模型执行第一步
                game_board = _initialize_game_board(board)  # 初始化 AlphaZero 的棋盘
                ai_action = ai_player.get_action(game_board)  # 获取 AlphaZero 的第一步
                ai_x, ai_y = game_board.move_to_location(ai_action)  # 转换 AlphaZero 返回的坐标
                board[ai_x][ai_y] = 'black'  # AI 落下黑子

            # 更新游戏状态
            board[ai_x][ai_y] = 'black'  # X 为行，Y 为列，先横后纵
            games[session_id]['current_player'] = 'white'

            print(f"AI placed black piece at ({ai_x}, {ai_y}) for session ID: {session_id}")

            # 发送 AI 的落子信息给客户端
            emit('updateBoard', {'board': games[session_id]['board'], 'next_turn': 'white'}, broadcast=True)
            # emit('aiMove', {'x': int(ai_x), 'y': int(ai_y), 'player': 'black'}, broadcast=True)
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

            # 获取当前游戏状态
            game = games[session_id]
            board = game['board']

            # 更新棋盘
            print("board[x][y]", board[x][y])
            print("player", player)
            if board[x][y] == '':
                board[x][y] = player
                game['current_player'] = 'white' if game['current_player'] == 'black' else 'black'
                print("game.current_player", game['current_player'])
                # 检查玩家是否获胜
                if not check_and_emit_winner(session_id, x, y, player):
                    print("AI is making its move...")
                    ai_move(session_id, game['current_player'])  # AI 下棋
                # 确保 AI 的棋盘状态被更新
                if ai_source == 'source':
                    ai_instance.boardMap = _convert_board_to_source_format(board)
            else:
                print(f"Invalid move: Position ({x}, {y}) is already occupied for session ID: {session_id}")
    except Exception as e:
        print(f"Error during player move: {str(e)}")
        disconnect()


def ai_move(session_id, ai_player_color):
    if session_id not in games:
        print(f"[ERROR] No game found for session ID: {session_id}")
        return

    print(f"[INFO] AI is calculating its next move for session ID: {session_id}")

    board = games[session_id]['board']

    try:
        if ai_source == 'source':
            # 更新 AI 实例的棋盘状态
            ai_instance.boardMap = _convert_board_to_source_format(board)
            # 使用 AI 的 get_action 方法获取下一步动作
            move_i, move_j = ai_instance.get_action()
            print(f"[DEBUG] AI (source) chose position: ({move_i}, {move_j})")
        else:
            game_board = _initialize_game_board(board)
            ai_action = ai_player.get_action(game_board)
            move_i, move_j = game_board.move_to_location(ai_action)
            print(f"[DEBUG] AI (AlphaZero) chose position: ({move_i}, {move_j})")

        # 验证和执行移动
        if 0 <= move_i < len(board) and 0 <= move_j < len(board[0]) and board[move_i][move_j] == '':
            board[move_i][move_j] = ai_player_color
            next_turn = 'black' if ai_player_color == 'white' else 'white'
            games[session_id]['current_player'] = next_turn
            print(f"[INFO] AI placed {ai_player_color} piece at ({move_i}, {move_j})")

            # 检查获胜条件并更新棋盘
            if not check_and_emit_winner(session_id, move_i, move_j, ai_player_color):
                emit('updateBoard', {
                    'board': games[session_id]['board'],
                    'next_turn': next_turn
                }, broadcast=True)
                print(f"[INFO] Next turn: {next_turn}")
        else:
            print(f"[ERROR] AI calculated an invalid move: ({move_i}, {move_j})")

    except Exception as e:
        print(f"[ERROR] Exception occurred during AI move calculation: {str(e)}")



# 检查胜赢条件
def check_winner(board, x, y, player):
    directions = [
        (0, 1),  # 水平方向
        (1, 0),  # 垂直方向
        (1, 1),  # 主对角线
        (1, -1)  # 副对角线
    ]

    for dx, dy in directions:
        count = 1
        i, j = x + dx, y + dy
        while 0 <= i < board_size and 0 <= j < board_size and board[i][j] == player:
            count += 1
            i += dx
            j += dy

        i, j = x - dx, y - dy
        while 0 <= i < board_size and 0 <= j < board_size and board[i][j] == player:
            count += 1
            i -= dx
            j -= dy

        if count >= 5:
            print(f"{player} wins!")
            return player

    return None


# 在每次 AI 或玩家下棋后检查胜赢
def check_and_emit_winner(session_id, x, y, player):
    print("check_and_emit_winner(session_id, x, y, player):", session_id, x, y, player)
    winner = check_winner(games[session_id]['board'], x, y, player)
    if winner:
        games[session_id]['status'] = 'ended'
        games[session_id]['winner'] = winner
        emit('gameOver', {'winner': winner}, broadcast=True)
        print("check_and_emit_winner", "true")
        return True
    return False


# 初始化游戏棋盘状态，用于 AI 的计算
def _initialize_game_board(board):
    """根据当前棋盘状态初始化 Board 对象。
    """
    game_board = Board(width=board_size, height=board_size, n_in_row=5)
    game_board.init_board()

    # 将当前棋盘状态应用到 game_board
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] == 'black':
                game_board.do_move(game_board.location_to_move((i, j)))
            elif board[i][j] == 'white':
                game_board.do_move(game_board.location_to_move((i, j)))

    return game_board


def handle_reset_game():
    decoded_token = get_decoded_token_from_request()
    session_id = decoded_token.get('email')

    if session_id in games:
        # 重置游戏状态
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


def handle_logout():
    decoded_token = get_decoded_token_from_request()  # 获取用户的 session ID
    session_id = decoded_token.get('email')  # 假设 email 作为 session_id

    if session_id in games:
        del games[session_id]  # 删除用户的游戏状态
        print(f"Game data cleared for session ID: {session_id}")


# Helper function to convert the board format to source AI format
def _convert_board_to_source_format(board):
    source_board_map = [[0 for _ in range(len(board))] for _ in range(len(board))]
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 'black':
                source_board_map[i][j] = 1  # 黑子在 GomokuAI 中表示为 1
            elif board[i][j] == 'white':
                source_board_map[i][j] = -1  # 白子在 GomokuAI 中表示为 -1
    return source_board_map
