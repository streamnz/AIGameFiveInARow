import { io } from "socket.io-client";
import React, { useEffect, useState, useRef } from 'react';
import './Game.css';

const Game = () => {
    const [board, setBoard] = useState(Array(15).fill().map(() => Array(15).fill(null))); // 初始化15x15的棋盘
    const [currentPlayer, setCurrentPlayer] = useState('black'); // 当前玩家
    const [gameOver, setGameOver] = useState(false);
    const [winner, setWinner] = useState(null);
    const [playerColor, setPlayerColor] = useState(null); // 玩家选择的颜色
    const [opponentColor, setOpponentColor] = useState(null); // 对手的颜色

    // 使用 useRef 来持久化 WebSocket 连接
    const socketRef = useRef(null);

    useEffect(() => {
        // 使用 Socket.IO 连接到 WebSocket 服务器，指定服务器路径
        socketRef.current = io('http://127.0.0.1:5000');

        // 连接成功时的日志
        socketRef.current.on('connect', () => {
            console.log('Connected to WebSocket server');
        });

        // 监听服务器发送的 'move' 消息
        socketRef.current.on('move', (message) => {
            if (message) {
                console.log('Received move:', message);
                const { x, y, player } = message;
                handleMove(x, y, player, false); // 从服务器接收的移动不发送到服务器
            }
        });

        // 监听服务器发送的 'gameOver' 消息
        socketRef.current.on('gameOver', (message) => {
            if (message) {
                console.log('Game over:', message);
                setWinner(message.winner);
                setGameOver(true);
            }
        });

        // 监听断开连接的日志
        socketRef.current.on('disconnect', () => {
            console.log('Disconnected from WebSocket server');
        });

        return () => {
            socketRef.current.disconnect(); // 在组件卸载时关闭 WebSocket 连接
        };
    }, []);

    // 处理棋盘点击和移动
    const handleMove = (x, y, player, sendToServer = true) => {
        if (!gameOver && board[x][y] === null) {
            const newBoard = board.map((row, rowIndex) =>
                row.map((cell, colIndex) => (rowIndex === x && colIndex === y ? player : cell))
            );
            setBoard(newBoard);
            setCurrentPlayer(currentPlayer === 'black' ? 'white' : 'black');

            // 发送棋子位置到服务器
            if (sendToServer) {
                console.log('Sending move to server:', { x, y, player });
                socketRef.current.emit('move', { x, y, player });
            }

            // 判断是否有玩家胜利
            checkWinner(newBoard, x, y, player);
        }
    };

    // 检查胜负条件
    const checkWinner = (newBoard, x, y, player) => {
        const directions = [
            [0, 1], [1, 0], [1, 1], [1, -1] // 水平，垂直，主对角线，副对角线
        ];

        for (let [dx, dy] of directions) {
            let count = 1;

            // 向一个方向检查
            for (let dir = 1; dir >= -1; dir -= 2) {
                let nx = x + dir * dx;
                let ny = y + dir * dy;

                while (nx >= 0 && nx < 15 && ny >= 0 && ny < 15 && newBoard[nx][ny] === player) {
                    count++;
                    nx += dir * dx;
                    ny += dir * dy;
                }
            }

            if (count >= 5) {
                setWinner(player);
                setGameOver(true);
                socketRef.current.emit('gameOver', { winner: player });
                return;
            }
        }
    };

    const handleCellClick = (x, y) => {
        // 只有玩家执棋时，才能点击棋盘进行操作
        if (!gameOver && board[x][y] === null && currentPlayer === playerColor) {
            handleMove(x, y, currentPlayer); // 点击时移动，并发送到服务器
        }
    };

    // 选择棋子颜色
    const handleColorSelection = (color) => {
        setPlayerColor(color);
        setOpponentColor(color === 'black' ? 'white' : 'black'); // 对手执另一颜色
        console.log(`Player selected ${color}`);
    };

    if (!playerColor) {
        // 玩家还没有选择执棋颜色时显示的界面
        return (
            <div className="game-container">
                <h2>Select your color</h2>
                <button onClick={() => handleColorSelection('black')}>Play as Black</button>
                <button onClick={() => handleColorSelection('white')}>Play as White</button>
            </div>
        );
    }

    return (
        <div className="game-container">
            <h2>Gomoku Game</h2>
            {gameOver ? <h3>Winner: {winner}</h3> : <h3>Current Player: {currentPlayer === playerColor ? 'You' : 'Opponent'}</h3>}
            <div className="board">
                {board.map((row, rowIndex) => (
                    <div key={rowIndex} className="row">
                        {row.map((cell, colIndex) => (
                            <div
                                key={colIndex}
                                className={`cell ${cell}`}
                                onClick={() => handleCellClick(rowIndex, colIndex)}
                            >
                                {cell && <div className={`piece ${cell}`}></div>}
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Game;
