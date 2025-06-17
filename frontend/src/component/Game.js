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
        console.log("=== Game Over Debug ===");
        console.log("Winner from server:", message.winner);
        console.log("Player color:", playerColor);
        console.log("Match result:", message.winner === playerColor ? "PLAYER WINS" : "AI WINS");
        console.log("======================");
        
        setWinner(message.winner);
        setGameOver(true);
        setIsWaitingForAI(false); // 游戏结束，停止等待AI
    }, [playerColor]);

    // 更新棋盘状态并根据当前玩家的颜色更新 currentPlayer
    const handleUpdateBoard = useCallback(({board: newBoard, next_turn}) => {
        console.log("handleUpdateBoard next_turn", next_turn);
        setCurrentPlayer(next_turn); // 后端返回当前回合的玩家
        setBoard(newBoard);
        setIsWaitingForAI(false); // AI已下完
    }, []);

    useEffect(() => {
        const jwtToken = localStorage.getItem("jwtToken");
        
        // 检查token是否存在
        if (!jwtToken) {
            console.log('No JWT token found, redirecting to login');
            // 触发登录模态框
            window.dispatchEvent(new CustomEvent('tokenExpired'));
            return;
        }

        socketRef.current = io(config.SOCKET_URL, {
            query: {token: jwtToken},
            reconnection: true,           // 启用重连
            reconnectionAttempts: 5,      // 最大重连次数
            reconnectionDelay: 1000,      // 重连延迟
            reconnectionDelayMax: 5000,   // 最大重连延迟
            timeout: 20000,               // 连接超时时间
        });

        socketRef.current.on("connect", () => {
            console.log("Connected to Socket.IO server");
        });

        socketRef.current.on("disconnect", (reason) => {
            console.log("Disconnected from Socket.IO server, reason:", reason);
            if (reason === 'io server disconnect') {
                // 服务器主动断开连接，可能是token过期
                console.log("Server disconnected, possibly due to token expiry");
                window.dispatchEvent(new CustomEvent('tokenExpired'));
            }
        });

        socketRef.current.on("connect_error", (error) => {
            console.error("Connection error:", error);
            if (error.message && error.message.includes('401')) {
                console.log("WebSocket connection failed due to authentication");
                window.dispatchEvent(new CustomEvent('tokenExpired'));
            }
        });

        socketRef.current.on("reconnect", (attemptNumber) => {
            console.log("Reconnected after", attemptNumber, "attempts");
        });

        socketRef.current.on("reconnect_error", (error) => {
            console.error("Reconnection error:", error);
        });

        socketRef.current.on("reconnect_failed", () => {
            console.error("Failed to reconnect after maximum attempts");
            window.dispatchEvent(new CustomEvent('tokenExpired'));
        });

        socketRef.current.on("error", (error) => {
            console.error("Socket error:", error);
            if (error.message && (error.message.includes('expired') || error.message.includes('Authentication failed'))) {
                console.log("Authentication error from server");
                window.dispatchEvent(new CustomEvent('tokenExpired'));
            }
        });

        socketRef.current.on("gameOver", handleGameOver);
        socketRef.current.on("updateBoard", handleUpdateBoard);

        return () => {
            if (socketRef.current) {
                socketRef.current.off("gameOver", handleGameOver);
                socketRef.current.off("updateBoard", handleUpdateBoard);
                socketRef.current.off("connect");
                socketRef.current.off("disconnect");
                socketRef.current.off("connect_error");
                socketRef.current.off("reconnect");
                socketRef.current.off("reconnect_error");
                socketRef.current.off("reconnect_failed");
                socketRef.current.off("error");
                socketRef.current.disconnect();
            }
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

    // 只关闭弹窗，不重置游戏状态
    const handleCloseModal = () => {
        setWinner(null);  // 只清除获胜者显示，关闭弹窗
    };

    // 开始新游戏，重置所有状态
    const handleNewGame = () => {
        // 先通知后端重置游戏
        socketRef.current.emit("resetGame");
        
        // 重置游戏状态
        setBoard(Array(15).fill(null).map(() => Array(15).fill(null)));
        setPlayerColor(null);  // 重置玩家颜色，显示选择页面
        setCurrentPlayer(null);
        setGameOver(false);
        setWinner(null);  // 最后再清除获胜者显示
    };

    const handleColorSelection = (color) => {
        setPlayerColor(color);
        if (color === "black") {
            // 玩家选择黑子，自己先下
            setCurrentPlayer("black");
        } else if (color === "white") {
            // 玩家选择白子，AI先下
            setCurrentPlayer("black"); // AI 使用黑子先手
            setIsWaitingForAI(true); // 设置等待AI状态
            
            // 确保 WebSocket 连接存在
            if (socketRef.current && socketRef.current.connected) {
                socketRef.current.emit("aiFirstMove"); // 触发AI第一步
            } else {
                console.error("WebSocket connection lost, attempting to reconnect...");
                // 重新连接 WebSocket
                const jwtToken = localStorage.getItem("jwtToken");
                socketRef.current = io(config.SOCKET_URL, {
                    query: {token: jwtToken},
                });
                
                // 重新绑定事件处理器
                socketRef.current.on("connect", () => {
                    console.log("Reconnected to Socket.IO server");
                    socketRef.current.emit("aiFirstMove"); // 重新连接后触发AI第一步
                });
                
                socketRef.current.on("gameOver", handleGameOver);
                socketRef.current.on("updateBoard", handleUpdateBoard);
            }
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
                    <div className="winner-announcement">
                        <div className="winner-crown">👑</div>
                        <h3 className="winner-text">
                            {winner === playerColor ? (
                                <span className="winner-you">Congratulations! You Won!</span>
                            ) : (
                                <span className="winner-ai">AI Wins This Round!</span>
                            )}
                        </h3>
                        <div className="winner-subtext">
                            {winner === playerColor ? 
                                "Your strategic brilliance has led you to victory!" :
                                "Don't give up! Challenge the AI again!"}
                        </div>
                        <div className="debug-info" style={{fontSize: '12px', color: '#666', marginTop: '10px'}}>
                            Debug: winner="{winner}", playerColor="{playerColor}", match={winner === playerColor ? 'YES' : 'NO'}
                        </div>
                    </div>
                    <div className="game-board-container">
                        {renderBoard()}
                        <button
                            className="new-game-button"
                            onClick={handleNewGame}
                        >
                            Start New Game
                        </button>
                    </div>
                </>
            ) : (
                <>
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
                    <div className="game-board-container">
                        {renderBoard()}
                    </div>
                </>
            )}
            {gameOver && winner && <WinnerModal
                winner={winner}
                playerColor={playerColor}
                onClose={handleCloseModal}
            />}
        </div>
    );
});

export default Game;
