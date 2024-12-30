from flask_socketio import emit, disconnect
import threading
from source.gomoku import ai_move
from source.AI import GomokuAI  # 导入 GomokuAI 类
from utils.jwt_util import get_decoded_token_from_request, decode_jwt_token

# 15x15 棋盘尺寸
board_size = 15

games = {}
games_lock = threading.Lock()


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
                    "winner": None,
                    "ai": GomokuAI()
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
        if session_id not in games:
            print(f"[ERROR] No game found for session ID: {session_id}")
            return
        ai = games[session_id]['ai']
        with games_lock:
            ai.firstMove()
            ai.turn *= -1
            print(f"[INFO] AI first move for session ID: {session_id}")
            board = games[session_id]['board']
            games[session_id]['ai_player_color'] = 'black'
            ai_player_color = games[session_id]['ai_player_color']

            # 验证和执行移动
            if 0 <= ai.currentI < len(board) and 0 <= ai.currentJ < len(board[0]) and board[ai.currentI][
                ai.currentJ] == '':
                board[ai.currentI][ai.currentJ] = ai_player_color
                next_turn = 'black' if ai_player_color == 'white' else 'white'
                games[session_id]['current_player'] = next_turn
                print(f"[INFO] AI placed {ai_player_color} piece at ({ai.currentI}, {ai.currentJ})")

                # 检查获胜条件并更新棋盘
                if not check_and_emit_winner(session_id, ai.currentI, ai.currentJ, ai_player_color):
                    emit('updateBoard', {
                        'board': games[session_id]['board'],
                        'next_turn': next_turn
                    }, broadcast=True)
                    print(f"[INFO] Next turn: {next_turn}")
                else:
                    print(f"[ERROR] AI calculated an invalid move: ({ai.currentI}, {ai.currentJ})")

    except Exception as e:
        print(f"Error during AI first move: {str(e)}")
        disconnect()


# 处理玩家的走子动作
def handle_player_move(data):
    try:
        decoded_token = get_decoded_token_from_request()
        session_id = decoded_token.get('email')
        ai = games[session_id]['ai']
        ai.turn *= -1
        with games_lock:
            if session_id not in games:
                print(f"No game found for session ID: {session_id}")
                return

            move_i, move_j = data['x'], data['y']
            player = data['player']

            print(f"Player {player} placed piece at ({move_i}, {move_j}) for session ID: {session_id}")

            # 更新 AI 的棋盘状态
            ai.boardValue = ai.evaluate(move_i, move_j, ai.boardValue, -1, ai.nextBound)
            ai.updateBound(move_i, move_j, ai.nextBound)
            ai.currentI, ai.currentJ = move_i, move_j
            # Make the move and update zobrist hash
            ai.setState(move_i, move_j, ai.turn)
            ai.rollingHash ^= ai.zobristTable[move_i][move_j][1]
            ai.emptyCells -= 1

            # 获取当前游戏状态
            game = games[session_id]
            board = game['board']

            # 更新棋盘
            print("board[x][y]", board[move_i][move_j])
            print("player", player)
            if board[move_i][move_j] == '':
                board[move_i][move_j] = player
                game['current_player'] = 'white' if game['current_player'] == 'black' else 'black'
                print("game.current_player", game['current_player'])
                # 检查玩家是否获胜
                if not check_and_emit_winner(session_id, move_i, move_j, player):
                    print("AI is making its move...")
                    my_ai_move(session_id, game['current_player'])  # AI 下棋
            else:
                print(f"Invalid move: Position ({move_i}, {move_j}) is already occupied for session ID: {session_id}")
    except Exception as e:
        print(f"Error during player move: {str(e)}")
        disconnect()


def my_ai_move(session_id, ai_player_color):
    if session_id not in games:
        print(f"[ERROR] No game found for session ID: {session_id}")
        return
    print(f"[INFO] AI is calculating its next move for session ID: {session_id}")

    try:
        board = games[session_id]['board']
        ai = games[session_id]['ai']
        ai.turn = 1
        move_i, move_j = ai_move(ai)
        print(f"[DEBUG] AI (source) chose position: ({move_i}, {move_j})")
        ai.setState(move_i, move_j, ai.turn)
        ai.rollingHash ^= ai.zobristTable[move_i][move_j][0]
        ai.emptyCells -= 1
        ai.turn *= -1

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


def handle_reset_game():
    decoded_token = get_decoded_token_from_request()
    session_id = decoded_token.get('email')

    if session_id in games:
        # 重置游戏状态
        games[session_id] = {
            "board": [['' for _ in range(board_size)] for _ in range(board_size)],
            "current_player": "black",
            "status": "ongoing",
            "winner": None,
            "ai": GomokuAI()
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


