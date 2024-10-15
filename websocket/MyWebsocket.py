from flask_socketio import emit
from ai.human_play import PolicyValueNet
from ai.mcts_alphaZero import MCTSPlayer
from ai.game import Board, Game
import torch

# 15x15 棋盘
board_size = 15
board = [['' for _ in range(board_size)] for _ in range(board_size)]
current_player = 'black'

# 设置AI模型的路径
model_file = './ai/current_policy_15_15_5.model2'
use_gpu = torch.cuda.is_available()  # 检查是否有 GPU

# 初始化 AI 使用 PolicyValueNet 和 MCTSPlayer
policy_value_net = PolicyValueNet(board_size, board_size, model_file=model_file, use_gpu=use_gpu)
ai_player = MCTSPlayer(policy_value_net.policy_value_fn, c_puct=5, n_playout=400)


# 客户端连接时的处理逻辑
def handle_connect():
    print("Client connected")


# 客户端断开连接时的处理逻辑
def handle_disconnect():
    print("Client disconnected")


# 处理客户端选择白棋的情况，AI 先下第一步
def handle_ai_first_move():
    global current_player
    global board

    print("AI starts first move (black)")

    # AI 下第一步黑棋
    game_board = Board(width=board_size, height=board_size, n_in_row=5)
    game_board.init_board()

    ai_action = ai_player.get_action(game_board)  # AI 计算下一步
    ai_x, ai_y = game_board.move_to_location(ai_action)

    board[int(ai_x)][int(ai_y)] = 'black'  # AI 落子为黑棋
    current_player = 'white'  # 轮到玩家下棋

    print(f"AI placed black piece at ({ai_x}, {ai_y})")

    # 发送 AI 的落子信息给客户端
    emit('aiMove', {'x': int(ai_x), 'y': int(ai_y), 'player': 'black'}, broadcast=True)


# 处理玩家的走子动作
def handle_player_move(data):
    global current_player
    x, y = data['x'], data['y']
    player = data['player']

    print(f"Player {player} placed piece at ({x}, {y})")

    # 更新棋盘
    if board[x][y] == '':
        board[x][y] = player
        current_player = 'white' if current_player == 'black' else 'black'

        # 检查玩家是否获胜
        if not check_and_emit_winner(x, y, player):
            print("AI is making its move...")
            ai_move()  # AI 下棋
    else:
        print(f"Invalid move: Position ({x}, {y}) is already occupied")


# AI 下棋逻辑
def ai_move():
    global current_player
    global board

    print("AI is calculating its next move...")

    # AI 计算下一步
    game_board = Board(width=board_size, height=board_size, n_in_row=5)
    game_board.init_board()

    # 将棋盘状态应用到 AI 计算的棋盘中
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] == 'black':
                game_board.do_move(game_board.location_to_move([i, j]))
            elif board[i][j] == 'white':
                game_board.do_move(game_board.location_to_move([i, j]))

    # AI 落子
    ai_action = ai_player.get_action(game_board)
    ai_x, ai_y = game_board.move_to_location(ai_action)
    board[ai_x][ai_y] = 'white'  # AI 落子为白棋
    current_player = 'black'  # 轮到玩家

    print(f"AI placed white piece at ({ai_x}, {ai_y})")

    # 检查 AI 是否获胜
    if not check_and_emit_winner(ai_x, ai_y, 'white'):
        emit('aiMove', {'x': int(ai_x), 'y': int(ai_y), 'player': 'white'}, broadcast=True)


# 检查胜负条件
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


# 在每次 AI 或玩家下棋后检查胜负
def check_and_emit_winner(x, y, player):
    winner = check_winner(board, x, y, player)
    if winner:
        emit('gameOver', {'winner': winner}, broadcast=True)
        return True
    return False
