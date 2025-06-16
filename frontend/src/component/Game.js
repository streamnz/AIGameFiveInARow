import React, {useEffect, useState, useRef, useCallback} from "react";
import {io} from "socket.io-client";
import "./Game.css";
import WinnerModal from "./WinnerModal"; // 引入 WinnerModal 组件
import config from '../config/config'; // 引入统一配置

const Game = React.memo(() => {
    const [board, setBoard] = useState(Array(15).fill(null).map(() => Array(15).fill(null)));
    const [currentPlayer, setCurrentPlayer] = useState("black");
    const [gameOver, setGameOver] = useState(false);
    const [winner, setWinner] = useState(null);
    const [playerColor, setPlayerColor] = useState(null);
    const [hoveredPosition, setHoveredPosition] = useState(null);
    const socketRef = useRef(null);
    const boardRef = useRef(null);
    const [isWaitingForAI, setIsWaitingForAI] = useState(false);

    const renderCount = useRef(0);

    useEffect(() => {
        renderCount.current += 1;
        console.log("Game component rendered", renderCount.current, "times");
    }, []);

    // 处理游戏结束
    const handleGameOver = useCallback((message) => {
        setWinner(message.winner,);
        setGameOver(true);
        setIsWaitingForAI(false); // 游戏结束，停止等待AI
    }, []);

    // 更新棋盘状态并根据当前玩家的颜色更新 currentPlayer
    const handleUpdateBoard = useCallback(({board: newBoard, next_turn}) => {
        console.log("handleUpdateBoard next_turn", next_turn);
        setCurrentPlayer(next_turn); // 后端返回当前回合的玩家
        setBoard(newBoard);
        setIsWaitingForAI(false); // AI已下完
    }, []);

    useEffect(() => {
        const jwtToken = localStorage.getItem("jwtToken");
        socketRef.current = io(config.SOCKET_URL, {
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
                // 如果是用户下棋，落子后等待AI
                if (player === playerColor) {
                    setIsWaitingForAI(true);
                }
            }
        } else {
            console.log("Invalid move!");
        }
    }, [board, gameOver, playerColor]);

    const handleBoardClick = useCallback((event) => {
        if (gameOver) {
            alert("Game is over!");
            return;
        }
        
        if (currentPlayer !== playerColor) {
            alert("It's not your turn! Please wait for the opponent.");
            return;
        }

        const rect = boardRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // 计算最近的交叉点
        const cellSize = rect.width / 14; // 14个格子，15个交叉点
        const col = Math.round(x / cellSize);
        const row = Math.round(y / cellSize);
        
        // 确保在有效范围内
        if (row >= 0 && row < 15 && col >= 0 && col < 15) {
            if (board[row][col] === "" || board[row][col] === null) {
                handleMove(row, col, currentPlayer);
            } else {
                alert("Invalid move");
            }
        }
    }, [board, currentPlayer, playerColor, gameOver, handleMove]);

    const handleBoardMouseMove = useCallback((event) => {
        if (gameOver || currentPlayer !== playerColor) {
            setHoveredPosition(null);
            return;
        }

        const rect = boardRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // 计算最近的交叉点
        const cellSize = rect.width / 14;
        const col = Math.round(x / cellSize);
        const row = Math.round(y / cellSize);
        
        // 确保在有效范围内并且位置为空
        if (row >= 0 && row < 15 && col >= 0 && col < 15 && !board[row][col]) {
            setHoveredPosition({ row, col });
        } else {
            setHoveredPosition(null);
        }
    }, [board, currentPlayer, playerColor, gameOver]);

    const handleBoardMouseLeave = useCallback(() => {
        setHoveredPosition(null);
    }, []);

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
            <div 
                className="gomoku-game-board" 
                ref={boardRef}
                onClick={handleBoardClick}
                onMouseMove={handleBoardMouseMove}
                onMouseLeave={handleBoardMouseLeave}
            >
                <div className="board-grid-lines">
                    {/* 绘制横线 */}
                    {[...Array(15)].map((_, i) => (
                        <div key={`h-${i}`} className="horizontal-line" style={{ top: `${(i / 14) * 100}%` }} />
                    ))}
                    {/* 绘制竖线 */}
                    {[...Array(15)].map((_, i) => (
                        <div key={`v-${i}`} className="vertical-line" style={{ left: `${(i / 14) * 100}%` }} />
                    ))}
                    {/* 绘制星位点 */}
                    {[3, 7, 11].map(row => 
                        [3, 7, 11].map(col => (
                            <div 
                                key={`star-${row}-${col}`} 
                                className="star-point" 
                                style={{ 
                                    top: `${(row / 14) * 100}%`, 
                                    left: `${(col / 14) * 100}%` 
                                }} 
                            />
                        ))
                    )}
                </div>
                {/* 棋子层 */}
                <div className="pieces-layer">
                    {board.map((row, rowIndex) => 
                        row.map((cell, colIndex) => 
                            cell && (
                                <div
                                    key={`piece-${rowIndex}-${colIndex}`}
                                    className={`gomoku-piece gomoku-piece-${cell}`}
                                    style={{
                                        top: `${(rowIndex / 14) * 100}%`,
                                        left: `${(colIndex / 14) * 100}%`
                                    }}
                                />
                            )
                        )
                    )}
                    {/* 悬停预览 */}
                    {hoveredPosition && (
                        <div
                            className={`gomoku-piece gomoku-piece-preview gomoku-piece-${playerColor}`}
                            style={{
                                top: `${(hoveredPosition.row / 14) * 100}%`,
                                left: `${(hoveredPosition.col / 14) * 100}%`
                            }}
                        />
                    )}
                </div>
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
                    <h3 className="winner-text">Winner: {winner}</h3>
                </>
            ) : (
                <h3 className="dynamic-player-tip">
                    {isWaitingForAI ? (
                        <>AI ({currentPlayer === playerColor ? (playerColor === "black" ? "white" : "black") : currentPlayer}) is playing<span className="dot-flash">...</span></>
                    ) : (
                        currentPlayer === playerColor ? (
                            <>You ({playerColor}) is playing<span className="dot-flash">...</span></>
                        ) : (
                            <>AI ({currentPlayer}) is playing<span className="dot-flash">...</span></>
                        )
                    )}
                </h3>
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
