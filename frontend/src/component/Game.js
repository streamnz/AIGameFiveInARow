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
    const [finalWinner, setFinalWinner] = useState(null); // 保存最终获胜者，不会被清空
    const [playerColor, setPlayerColor] = useState(null);
    const [hoveredPosition, setHoveredPosition] = useState(null);
    const socketRef = useRef(null);
    const boardRef = useRef(null);
    const [isWaitingForAI, setIsWaitingForAI] = useState(false);
    const [socketConnected, setSocketConnected] = useState(false);
    const [showWinnerModal, setShowWinnerModal] = useState(false); // 控制弹窗显示

    const renderCount = useRef(0);

    useEffect(() => {
        renderCount.current += 1;
        console.log("Game component rendered", renderCount.current, "times");
    }, []);



    // 初始化WebSocket连接 - 只在组件挂载时执行一次
    useEffect(() => {
        const jwtToken = localStorage.getItem("jwtToken");
        
        // 检查token是否存在
        if (!jwtToken) {
            console.log('No JWT token found, redirecting to login');
            // 触发登录模态框
            window.dispatchEvent(new CustomEvent('tokenExpired'));
            return;
        }

        // 避免重复连接
        if (socketRef.current && socketRef.current.connected) {
            console.log("Socket already connected, skipping initialization");
            return;
        }

        console.log("Initializing WebSocket connection");
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
            setSocketConnected(true);
        });

        socketRef.current.on("disconnect", (reason) => {
            console.log("Disconnected from Socket.IO server, reason:", reason);
            setSocketConnected(false);
            
            if (reason === 'io server disconnect') {
                // 服务器主动断开连接，可能是token过期
                console.log("Server disconnected, possibly due to token expiry");
                window.dispatchEvent(new CustomEvent('tokenExpired'));
            } else if (reason === 'transport close' || reason === 'transport error') {
                // 网络问题，尝试重连
                console.log("Network disconnection, will attempt to reconnect");
            }
        });

        socketRef.current.on("connect_error", (error) => {
            console.error("Connection error:", error);
            if (error.message && error.message.includes('401')) {
                console.log("WebSocket connection failed due to authentication");
                window.dispatchEvent(new CustomEvent('tokenExpired'));
            }
            setSocketConnected(false);
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
            setSocketConnected(false);
        });

        // 使用ref来绑定事件处理器，避免依赖问题
        const handleGameOverEvent = (message) => {
            console.log("Game Over - Winner:", message.winner);
            setWinner(message.winner);
            setFinalWinner(message.winner);
            setGameOver(true);
            setShowWinnerModal(true);
            setIsWaitingForAI(false);
        };

        const handleUpdateBoardEvent = ({board: newBoard, next_turn}) => {
            console.log("Board updated - Next turn:", next_turn);
            setCurrentPlayer(next_turn);
            setBoard(newBoard);
            setIsWaitingForAI(false);
        };

        socketRef.current.on("gameOver", handleGameOverEvent);
        socketRef.current.on("updateBoard", handleUpdateBoardEvent);

        return () => {
            if (socketRef.current) {
                console.log("Cleaning up WebSocket connection");
                socketRef.current.off("gameOver");
                socketRef.current.off("updateBoard");
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
    }, []); // 空依赖数组，只在组件挂载时执行一次

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
        setShowWinnerModal(false);  // 只关闭弹窗
        // 保持 gameOver=true, finalWinner 不变，这样主页面会显示正确的获胜者
    };

    // 开始新游戏，重置所有状态
    const handleNewGame = () => {
        // 先通知后端重置游戏
        if (socketRef.current && socketRef.current.connected) {
            socketRef.current.emit("resetGame");
        }
        
        // 重置游戏状态
        setBoard(Array(15).fill(null).map(() => Array(15).fill(null)));
        setPlayerColor(null);  // 重置玩家颜色，显示选择页面
        setCurrentPlayer(null);
        setGameOver(false);
        setWinner(null);
        setFinalWinner(null);  // 清除最终获胜者
        setShowWinnerModal(false);  // 关闭弹窗
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
            
            // 确保 WebSocket 连接存在并触发AI第一步
            console.log("Requesting AI first move, socket connected:", socketConnected);
            if (socketRef.current && socketConnected) {
                console.log("Emitting aiFirstMove event");
                socketRef.current.emit("aiFirstMove"); // 触发AI第一步
            } else {
                console.warn("WebSocket not connected, will retry when connection is established");
                // 设置一个短暂的延迟重试
                setTimeout(() => {
                    if (socketRef.current && socketRef.current.connected) {
                        console.log("Retrying aiFirstMove after delay");
                        socketRef.current.emit("aiFirstMove");
                    } else {
                        console.error("WebSocket still not connected after delay");
                    }
                }, 1000);
            }
        }
    };

    const renderBoard = () => {
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
                            {finalWinner && finalWinner === playerColor ? (
                                <span className="winner-you">Congratulations! You Won!</span>
                            ) : finalWinner && finalWinner !== playerColor && finalWinner !== '' ? (
                                <span className="winner-ai">AI Wins This Round!</span>
                            ) : (
                                <span className="winner-unknown">Game Over - Unknown Result</span>
                            )}
                        </h3>
                        <div className="winner-subtext">
                            {finalWinner && finalWinner === playerColor ? 
                                "Your strategic brilliance has led you to victory!" :
                                finalWinner && finalWinner !== playerColor && finalWinner !== '' ?
                                "Don't give up! Challenge the AI again!" :
                                "Something went wrong with the game result."}
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
                        {!socketConnected ? (
                            <>🔴 Connection Lost - Reconnecting<span className="dot-flash">...</span></>
                        ) : isWaitingForAI ? (
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
            {showWinnerModal && winner && <WinnerModal
                winner={winner}
                playerColor={playerColor}
                onClose={handleCloseModal}
            />}
        </div>
    );
});

export default Game;
