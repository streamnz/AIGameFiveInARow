import React, {useEffect, useState, useRef, useCallback} from "react";
import {io} from "socket.io-client";
import "./Game.css";
import WinnerModal from "./WinnerModal"; // 引入 WinnerModal 组件

const GomokuCell = React.memo(({x, y, value, onClick}) => {
    return (
        <div className="gomoku-cell" onClick={() => onClick(x, y)}>
            {value === "black" && <div className="gomoku-piece gomoku-piece-black"></div>}
            {value === "white" && <div className="gomoku-piece gomoku-piece-white"></div>}
        </div>
    );
});
const Game = React.memo(() => {
    const [board, setBoard] = useState(Array(15).fill(null).map(() => Array(15).fill(null)));
    const [gameState, setGameState] = useState({
        currentPlayer: null,
        playerColor: null,
        canPlayerMove: false, // 合并后的状态
    });
    const [gameOver, setGameOver] = useState(false);
    const [winner, setWinner] = useState(null);
    const socketRef = useRef(null);

    const handleGameOver = useCallback((message) => {
        if (message && message.winner) {
            setWinner(message.winner);
        } else {
            setWinner("Draw or No Winner");
        }
        setGameOver(true);
    }, []);

    const handleUpdateBoard = useCallback(({board: newBoard, next_turn}) => {
        setBoard(newBoard);
        setGameState((prev) => ({
            ...prev,
            currentPlayer: next_turn,
            canPlayerMove: next_turn === prev.playerColor, // 更新合并后的状态
        }));
    }, []);

    useEffect(() => {
        const jwtToken = localStorage.getItem("jwtToken");
        socketRef.current = io("https://aigame.streamnz.com", {
            query: {token: jwtToken},
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
        if (gameOver) {
            alert("The Game is Over!");
            return;
        }
        if (board[x][y] === "" || board[x][y] === null) {
            const newBoard = board.map((row, rowIndex) =>
                row.map((cell, colIndex) => (rowIndex === x && colIndex === y ? player : cell))
            );
            setBoard(newBoard);
            if (sendToServer) {
                console.log("playerMove", {x, y, player});
                socketRef.current.emit("playerMove", {x, y, player});
                setGameState((prev) => ({
                    ...prev,
                    canPlayerMove: false, // 设置为false，等待AI响应
                }));
            }
        } else {
            console.log("Invalid move!");
        }
    }, [board, gameOver]);

    const handleCellClick = useCallback((x, y) => {
        if (gameOver) {
            alert("Game is over!");
            return;
        }
        if (!gameState.canPlayerMove) { // 使用合并后的状态
            alert("It's not your turn! Please wait for the AI.");
            return;
        }
        if (board[x][y] === "" || board[x][y] === null) {
            handleMove(x, y, gameState.currentPlayer);
        } else {
            alert("Invalid move");
        }
    }, [board, gameState, gameOver, handleMove]);

    const handleCloseModal = () => {
        setGameOver(false);
        setWinner(null);
        setBoard(Array(15).fill(null).map(() => Array(15).fill(null)));
        setGameState({
            currentPlayer: null,
            playerColor: null,
            canPlayerMove: false,
        });
        socketRef.current.emit("resetGame");
    };

    const handleColorSelection = (color) => {
        setGameState({
            currentPlayer: "black",
            playerColor: color,
            canPlayerMove: color === "black", // 初始设置
        });

        if (color === "white") {
            socketRef.current.emit("aiFirstMove");
        }
    };

    const renderBoard = () => {
        console.log("Rendering the board");
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

    if (!gameState.playerColor) {
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
                <>
                    <h3>Winner: {winner}</h3>
                </>
            ) : (
                <h3>Current Player: {gameState.canPlayerMove ? "You" : "Opponent"}</h3>
            )}
            {renderBoard()}
            {gameOver && <WinnerModal
                winner={winner}
                playerColor={gameState.playerColor}
                onClose={handleCloseModal}
            />}
        </div>
    );
});

export default Game;