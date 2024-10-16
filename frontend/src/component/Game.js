import React, { useEffect, useState, useRef, useCallback } from "react";
import { io } from "socket.io-client";
import "./Game.css";

// 单独的棋盘格子组件，使用 React.memo 防止不必要的重新渲染
const GomokuCell = React.memo(({ x, y, value, onClick }) => {
    return (
        <div className="gomoku-cell" onClick={() => onClick(x, y)}>
            {value === "black" && <div className="gomoku-piece gomoku-piece-black"></div>}
            {value === "white" && <div className="gomoku-piece gomoku-piece-white"></div>}
        </div>
    );
});

const Game = () => {
    const [board, setBoard] = useState(Array(15).fill().map(() => Array(15).fill(null))); // 初始化15x15的棋盘
    const [currentPlayer, setCurrentPlayer] = useState("black"); // 当前玩家
    const [gameOver, setGameOver] = useState(false);
    const [winner, setWinner] = useState(null);
    const [playerColor, setPlayerColor] = useState(null); // 玩家选择的颜色

    const socketRef = useRef(null);

    // WebSocket 连接与事件管理
    useEffect(() => {
        const jwtToken = localStorage.getItem('jwtToken'); // 从本地存储中获取 JWT token
        socketRef.current = io("http://127.0.0.1:5000", {
            query: { token: jwtToken }, // 在连接时传递 token
        });

        socketRef.current.on("connect", () => {
            console.log("Connected to Socket.IO server");
        });

        const handleGameOver = (message) => {
            setWinner(message.winner);
            setGameOver(true);
        };

        const handleAiMove = ({ x, y, player }) => {
            console.log("AI Move", { x, y, player });
            handleMove(x, y, player, false); // AI 落子后更新棋盘
        };

        socketRef.current.on("gameOver", handleGameOver);
        socketRef.current.on("aiMove", handleAiMove);

        socketRef.current.on("disconnect", () => {
            console.log("Disconnected from Socket.IO server");
        });

        return () => {
            socketRef.current.off("gameOver", handleGameOver);
            socketRef.current.off("aiMove", handleAiMove);
            socketRef.current.disconnect();
        };
    }, []);

    // 处理玩家或AI的走子逻辑
    const handleMove = useCallback((x, y, player, sendToServer = true) => {
        if (x < 0 || x >= 15 || y < 0 || y >= 15 || !board[x]) {
            console.log("Invalid coordinates or board row undefined:", x, y);
            return;
        }

        if (!gameOver && board[x][y] === null) {
            const newBoard = board.map((row, rowIndex) =>
                row.map((cell, colIndex) => (rowIndex === x && colIndex === y ? player : cell))
            );
            console.log("handleMove newBoard", newBoard);
            setBoard(newBoard);
            setCurrentPlayer((prevPlayer) => (prevPlayer === "black" ? "white" : "black"));

            if (sendToServer) {
                socketRef.current.emit("playerMove", { x, y, player });
            }
        } else {
            console.log("Invalid move or game over.");
        }
    }, [board, gameOver]);

    const handleCellClick = useCallback((x, y) => {
        console.log("Cell clicked at:", x, y);
        if (currentPlayer !== playerColor) {
            alert("It's not your turn! Please wait for the opponent.");
            return;
        }

        if (board[x][y] === null) {
            handleMove(x, y, currentPlayer);
        } else {
            console.log("Invalid move or playerColor not set");
        }
    }, [board, currentPlayer, playerColor, handleMove]);

    // 玩家选择颜色
    const handleColorSelection = (color) => {
        setPlayerColor(color);
        if (color === 'white') {
            socketRef.current.emit("aiFirstMove");
        }
    };

    // 渲染棋盘
    const renderBoard = () => {
        return (
            <div className="gomoku-game-board">
                {board.map((row, rowIndex) => (
                    <div key={rowIndex} className="gomoku-row">
                        {row.map((cell, colIndex) => (
                            <GomokuCell
                                key={`${rowIndex}-${colIndex}`}
                                x={rowIndex}
                                y={colIndex}
                                value={cell}
                                onClick={handleCellClick}
                            />
                        ))}
                    </div>
                ))}
            </div>
        );
    };

    if (!playerColor) {
        return (
            <div className="gomoku-game-container">
                <h2>Select your color</h2>
                <button className="gomoku-player-select-white-black" onClick={() => handleColorSelection("black")}>Play as Black</button>
                <button className="gomoku-player-select-white-black" onClick={() => handleColorSelection("white")}>Play as White</button>
            </div>
        );
    }

    return (
        <div className="gomoku-game-container">
            <h2>Gomoku Game</h2>
            {gameOver ? <h3>Winner: {winner}</h3> : <h3>Current Player: {currentPlayer === playerColor ? "You" : "Opponent"}</h3>}
            {renderBoard()}
        </div>
    );
};

export default Game;
