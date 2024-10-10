import React, { useEffect, useState, useRef } from "react";
import { io } from "socket.io-client";
import "./Game.css";

const Game = () => {
    const [board, setBoard] = useState(Array(15).fill().map(() => Array(15).fill(null))); // 初始化15x15的棋盘
    const [currentPlayer, setCurrentPlayer] = useState("black"); // 当前玩家
    const [gameOver, setGameOver] = useState(false);
    const [winner, setWinner] = useState(null);
    const [playerColor, setPlayerColor] = useState(null); // 玩家选择的颜色
    const [opponentColor, setOpponentColor] = useState(null); // 对手的颜色

    const socketRef = useRef(null);
    const boardSize = 600; // 棋盘的大小
    const cellSize = 40; // 每个单元格的大小

    useEffect(() => {
        // 使用 Socket.IO 建立 WebSocket 连接
        socketRef.current = io("http://127.0.0.1:5000");

        socketRef.current.on("connect", () => {
            console.log("Connected to Socket.IO server");
        });

        // 监听来自服务器的移动
        socketRef.current.on("gameState", (message) => {
            console.log("Received move from server:", message);
            const { x, y, player } = message;
            handleMove(x, y, player, false); // 从服务器接收的移动不发送到服务器
        });

        // 监听游戏结束
        socketRef.current.on("gameOver", (message) => {
            console.log("Game over received from server:", message);
            setWinner(message.winner);
            setGameOver(true);
        });

        socketRef.current.on("disconnect", () => {
            console.log("Disconnected from Socket.IO server");
        });

        return () => {
            socketRef.current.disconnect();
        };
    }, []);

    // 处理移动
    const handleMove = (x, y, player, sendToServer = true) => {
        if (!gameOver && board[x][y] === null) {
            const newBoard = board.map((row, rowIndex) =>
                row.map((cell, colIndex) => (rowIndex === x && colIndex === y ? player : cell))
            );
            setBoard(newBoard);
            setCurrentPlayer(currentPlayer === "black" ? "white" : "black");

            if (sendToServer) {
                socketRef.current.emit("startGame", { x, y, player });
            }

            checkWinner(newBoard, x, y, player);
        } else {
            console.log("Invalid move or game over.");
        }
    };

    // 检查胜利条件
    const checkWinner = (newBoard, x, y, player) => {
        const directions = [
            [0, 1], [1, 0], [1, 1], [1, -1]
        ];

        for (let [dx, dy] of directions) {
            let count = 1;

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
                socketRef.current.emit("gameOver", { winner: player });
                return;
            }
        }
    };

    // 点击格子时的处理
    const handleCellClick = (event) => {
        const boardRect = event.target.getBoundingClientRect();
        const offsetX = event.clientX - boardRect.left;
        const offsetY = event.clientY - boardRect.top;

        // 计算最近的交叉点
        const x = Math.floor(offsetX / cellSize);
        const y = Math.floor(offsetY / cellSize);

        // 检查是否为玩家的回合并且该格子是否为空
        if (!gameOver && board[x][y] === null && currentPlayer === playerColor) {
            handleMove(x, y, currentPlayer);
        } else {
            console.log("Invalid move or not your turn.");
        }
    };

    // 玩家选择颜色
    const handleColorSelection = (color) => {
        setPlayerColor(color);
        setOpponentColor(color === "black" ? "white" : "black");
        console.log(`Player selected ${color}`);
    };

    // 如果没有选择棋子颜色，显示选择颜色的界面
    if (!playerColor) {
        return (
            <div className="game-container">
                <h2>Select your color</h2>
                <button className="player-select-white-black" onClick={() => handleColorSelection("black")}>Play as Black</button>
                <button className="player-select-white-black" onClick={() => handleColorSelection("white")}>Play as White</button>
            </div>
        );
    }

    return (
        <div className="game-container">
            <h2>Gomoku Game</h2>
            {gameOver ? <h3>Winner: {winner}</h3> :
                <h3>Current Player: {currentPlayer === playerColor ? "You" : "Opponent"}</h3>}
            <div className="game-board" onClick={handleCellClick}>
                {board.map((row, rowIndex) => (
                    <div key={rowIndex} className="row">
                        {row.map((cell, colIndex) => {
                            return (
                                <div key={colIndex} className={`cell`}>
                                    {cell && <div className={`piece ${cell}`}></div>}
                                </div>
                            );
                        })}
                    </div>
                ))}
            </div>

        </div>
    );
};

export default Game;
