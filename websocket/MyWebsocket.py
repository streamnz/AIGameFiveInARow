from flask_socketio import emit
from gradio import JSON

from source.AI import GomokuAI  # 导入 AI 类

# 15x15 棋盘
board = [['' for _ in range(15)] for _ in range(15)]
current_player = 'black'

# 初始化 AI
ai_player = GomokuAI()


# 客户端连接时的处理逻辑
def handle_connect():
    print("Client connected")


# 客户端断开连接时的处理逻辑
def handle_disconnect():
    print("Client disconnected")


# 处理客户端发来的下棋请求
def handle_start_game(data):
    print("handle_start_game")
    print(data)
    # global current_player
    # x, y = data['x'], data['y']
    # player = data['player']
    #
    # # 更新棋盘
    # if board[x][y] == '':
    #     board[x][y] = player
    #     ai_player.setState(x, y, 1 if player == 'black' else -1)
    #     current_player = 'white' if current_player == 'black' else 'black'
    #
    #     # 广播玩家的移动给所有客户端
    #     emit('gameState', {'x': x, 'y': y, 'player': player}, broadcast=True)
    #
    #     # 检查胜利条件
    #     winner = check_winner(board, x, y, player)
    #     if winner:
    #         emit('gameOver', {'winner': winner}, broadcast=True)
    #         return
    #
    #     # 如果轮到 AI，下棋并返回结果
    #     if current_player == 'white':
    #         ai_move()


# AI 执行下棋动作
def ai_move():
    global current_player
    ai_player.alphaBetaPruning(ai_player.depth, ai_player.boardValue, ai_player.nextBound, -float('inf'), float('inf'),
                               True)
    ai_x, ai_y = ai_player.currentI, ai_player.currentJ  # AI 计算的下一步
    board[ai_x][ai_y] = 'white'
    current_player = 'black'
    ai_player.setState(ai_x, ai_y, 1)

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
        while 0 <= i < 15 and 0 <= j < 15 and board[i][j] == player:
            count += 1
            i += dx
            j += dy

        i, j = x - dx, y - dy
        while 0 <= i < 15 and 0 <= j < 15 and board[i][j] == player:
            count += 1
            i -= dx
            j -= dy

        if count >= 5:
            return player

    return None
