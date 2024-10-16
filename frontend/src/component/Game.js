import React, { useEffect, useState, useRef, useCallback } from "react";
import { io } from "socket.io-client";
import "./Game.css";

const GomokuCell = React.memo(({ x, y, value, onClick }) => {
    return (
        <div className="gomoku-cell" onClick={() => onClick(x, y)}>
            {value === "black" && <div className="gomoku-piece gomoku-piece-black"></div>}
            {value === "white" && <div className="gomoku-piece gomoku-piece-white"></div>}
        </div>
    );
});

const Game = () => {
    const [board, setBoard] = useState(Array(15).fill(null).map(() => Array(15).fill(null)));
    const [currentPlayer, setCurrentPlayer] = useState("black");
    const [gameOver, setGameOver] = useState(false);
    const [winner, setWinner] = useState(null);
    const [playerColor, setPlayerColor] = useState(null);
    const socketRef = useRef(null);

    // 处理游戏结束
    const handleGameOver = useCallback((message) => {
        setWinner(message.winner);
        setGameOver(true);
    }, []);

    // 更新棋盘状态
    const handleUpdateBoard = useCallback(({ board: newBoard }) => {
        setBoard(newBoard);
        setCurrentPlayer((prevPlayer) => (prevPlayer === "black" ? "white" : "black"));
    }, []);

    useEffect(() => {
        const jwtToken = localStorage.getItem("jwtToken");
        socketRef.current = io("http://127.0.0.1:5000", {
            query: { token: jwtToken },
        });

        socketRef.current.on("connect", () => {
            console.log("Connected to Socket.IO server");
        });

        socketRef.current.on("gameOver", handleGameOver);
        socketRef.current.on("updateBoard", handleUpdateBoard);

        socketRef.current.on("disconnect", () => {
            console.log("Disconnected from Socket.IO server");
        });

        return () => {
            socketRef.current.off("gameOver", handleGameOver);
            socketRef.current.off("updateBoard", handleUpdateBoard);
            socketRef.current.disconnect();
        };
    }, [handleGameOver, handleUpdateBoard]);

    const handleMove = useCallback((x, y, player, sendToServer = true) => {
        if (x < 0 || x >= 15 || y < 0 || y >= 15 || !board[x]) {
            console.log("Invalid coordinates or board row undefined:", x, y);
            return;
        }

        if (!gameOver && board[x][y] === "") {
            const newBoard = board.map((row, rowIndex) =>
                row.map((cell, colIndex) => (rowIndex === x && colIndex === y ? player : cell))
            );
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
        if (gameOver) {
            alert("Game is over!");
            return;
        }

        if (currentPlayer !== playerColor) {
            alert("It's not your turn! Please wait for the opponent.");
            return;
        }
        console.log("handleCellClick", x, y,board[x][y]);
        if (board[x][y] === "" || board[x][y] === null) {
            handleMove(x, y, currentPlayer);
        } else {
            alert("Invalid move");
        }
    }, [board, currentPlayer, playerColor, gameOver, handleMove]);

    const handleColorSelection = (color) => {
        setPlayerColor(color);
        if (color === "white") {
            socketRef.current.emit("aiFirstMove");
        }
    };

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
                <button
                    className="gomoku-player-select-white-black"
                    onClick={() => handleColorSelection("black")}
                >
                    Play as Black
                </button>
                <button
                    className="gomoku-player-select-white-black"
                    onClick={() => handleColorSelection("white")}
                >
                    Play as White
                </button>
            </div>
        );
    }

    return (
        <div className="gomoku-game-container">
            <h2>Gomoku Game</h2>
            {gameOver ? (
                <h3>Winner: {winner}</h3>
            ) : (
                <h3>Current Player: {currentPlayer === playerColor ? "You" : "Opponent"}</h3>
            )}
            {renderBoard()}
        </div>
    );
};

export default Game;
