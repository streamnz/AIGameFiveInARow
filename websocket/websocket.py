from flask_socketio import SocketIO, send, emit

# 创建 SocketIO 对象
socketio = SocketIO()

# 15x15 棋盘
board = [['' for _ in range(15)] for _ in range(15)]
current_player = 'black'


# 客户端连接 WebSocket
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    send({'data': 'Connected to server'})


# 处理客户端发送的移动
@socketio.on('move')
def handle_move(data):
    global current_player
    x, y = data['x'], data['y']
    player = data['player']

    # 更新棋盘
    if board[x][y] == '':
        board[x][y] = player
        current_player = 'white' if current_player == 'black' else 'black'
        emit('move', {'x': x, 'y': y, 'player': player}, broadcast=True)

    # 检查胜利条件 (未实现)
    # winner = check_winner(board)
    # if winner:
    #     emit('gameOver', {'winner': winner}, broadcast=True)


def check_winner(board):
    # 在这里实现五子棋胜利逻辑
    pass
