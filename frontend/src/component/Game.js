import React, {useEffect, useState, useRef, useCallback} from "react";
import {io} from "socket.io-client";
import "./Game.css";
import WinnerModal from "./WinnerModal"; // 引入 WinnerModal 组件

const GomokuCell = React.memo(({x, y, value, onClick}) => {
    console.log("Rendering cell at", x, y);
    return (
        <div className="gomoku-cell" onClick={() => onClick(x, y)}>
            {value === "black" && <div className="gomoku-piece gomoku-piece-black"></div>}
            {value === "white" && <div className="gomoku-piece gomoku-piece-white"></div>}
        </div>
    );
});

const Game = React.memo(() => {
    const [board, setBoard] = useState(Array(15).fill(null).map(() => Array(15).fill(null)));
    const [currentPlayer, setCurrentPlayer] = useState("black");
    const [gameOver, setGameOver] = useState(false);
    const [winner, setWinner] = useState(null);
    const [playerColor, setPlayerColor] = useState(null);
    const socketRef = useRef(null);

    const renderCount = useRef(0);

    useEffect(() => {
        renderCount.current += 1;
        console.log("Game component rendered", renderCount.current, "times");
    }, []);

    // 处理游戏结束
    const handleGameOver = useCallback((message) => {
        setWinner(message.winner,);
        setGameOver(true);
    }, []);

    // 更新棋盘状态并根据当前玩家的颜色更新 currentPlayer
    const handleUpdateBoard = useCallback(({board: newBoard, next_turn}) => {
        console.log("handleUpdateBoard next_turn", next_turn);
        setCurrentPlayer(next_turn); // 后端返回当前回合的玩家
        setBoard(newBoard);
    }, []);

    useEffect(() => {
        const jwtToken = localStorage.getItem("jwtToken");
        socketRef.current = io("http://localhost:5050", {
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
            alert("The Game is Over!")
            return;
        }
        console.log("board[x][y]", board[x][y]);
        if (board[x][y] === "" || board[x][y] === null) {
            // 用户点击，提前显示点击效果
            const newBoard = board.map((row, rowIndex) =>
                row.map((cell, colIndex) => (rowIndex === x && colIndex === y ? player : cell))
            );
            setBoard(newBoard);
            if (sendToServer) {
                console.log("playerMove", {x, y, player})
                socketRef.current.emit("playerMove", {x, y, player});
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
        console.log("currentPlayer and playerColor", currentPlayer, playerColor)
        if (currentPlayer !== playerColor) {
            alert("It's not your turn! Please wait for the opponent.");
            return;
        }

        if (board[x][y] === "" || board[x][y] === null) {
            handleMove(x, y, currentPlayer);
        } else {
            alert("Invalid move");
        }
    }, [board, currentPlayer, playerColor, gameOver, handleMove]);

    // 关闭模态框，重置游戏状态并显示颜色选择页面
    const handleCloseModal = () => {
        setGameOver(false);
        setWinner(null);
        setBoard(Array(15).fill(null).map(() => Array(15).fill(null)));
        setPlayerColor(null);  // 重置玩家颜色，显示选择页面
        setCurrentPlayer(null);
        socketRef.current.emit("resetGame");  // 通知后端重置游戏
    };

    const handleColorSelection = (color) => {
        setPlayerColor(color);
        if (color === "black") {
            // 玩家选择黑子，自己先下
            setCurrentPlayer("black");
        } else if (color === "white") {
            // 玩家选择白子，AI先下，设置玩家为黑子
            setCurrentPlayer("white");
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
                <>
                    <h3>Winner: {winner}</h3>
                </>
            ) : (
                <h3>Current Player: {currentPlayer === playerColor ? "You" : "Opponent"}</h3>
            )}
            {renderBoard()}
            {/* 渲染 WinnerModal */}
            {gameOver && <WinnerModal
                winner={winner}
                playerColor={playerColor}  // 传递玩家颜色
                onClose={handleCloseModal}
            />}
        </div>
    );
});

export default Game;
