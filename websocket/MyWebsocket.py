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


# 处理客户端发来的下棋请求
def handle_start_game(data):
    """
    处理客户端请求开始游戏，初始化棋盘并开始游戏
    """
    global current_player
    print("handle_start_game")
    print(data)

    # 重置棋盘和游戏状态
    global board
    board = [['' for _ in range(board_size)] for _ in range(board_size)]
    current_player = 'black'

    emit('gameState', {'message': 'Game started!', 'board': board}, broadcast=True)


# AI 执行下棋动作
def ai_move():
    global current_player
    global board

    # 将当前棋盘状态转换为适合 AI 处理的格式
    game_board = Board(width=board_size, height=board_size, n_in_row=5)
    game_board.init_board()

    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] == 'black':
                game_board.do_move(game_board.location_to_move([i, j]), player=1)
            elif board[i][j] == 'white':
                game_board.do_move(game_board.location_to_move([i, j]), player=2)

    # AI 计算下一步
    ai_action = ai_player.get_action(game_board)

    # 将 AI 走子应用到棋盘
    ai_x, ai_y = game_board.move_to_location(ai_action)
    board[ai_x][ai_y] = 'white'
    current_player = 'black'

    # 通知前端 AI 的移动
    emit('gameState', {'x': ai_x, 'y': ai_y, 'player': 'white'}, broadcast=True)

    # 检查 AI 是否获胜
    winner = check_winner(board, ai_x, ai_y, 'white')
    if winner:
        emit('gameOver', {'winner': 'white'}, broadcast=True)


# 检查胜利条件
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
            return player

    return None


# 处理客户端发来的玩家走子请求
def handle_human_move(data):
    """
    处理玩家的走子动作
    """
    global current_player
    x, y = data['x'], data['y']
    player = data['player']

    # 更新棋盘
    if board[x][y] == '':
        board[x][y] = player
        current_player = 'white' if current_player == 'black' else 'black'

        # 广播玩家的移动给所有客户端
        emit('gameState', {'x': x, 'y': y, 'player': player}, broadcast=True)

        # 检查胜利条件
        winner = check_winner(board, x, y, player)
        if winner:
            emit('gameOver', {'winner': winner}, broadcast=True)
            return

        # 如果轮到 AI 下棋
        if current_player == 'white':
            ai_move()
