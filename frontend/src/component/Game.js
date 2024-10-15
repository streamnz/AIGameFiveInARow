import React, {useEffect, useState, useRef, useCallback, useMemo} from "react";
import {io} from "socket.io-client";
import "./Game.css";

const Game = () => {
    const [board, setBoard] = useState(Array(15).fill().map(() => Array(15).fill(null))); // 初始化15x15的棋盘
    const [currentPlayer, setCurrentPlayer] = useState("black"); // 当前玩家
    const [gameOver, setGameOver] = useState(false);
    const [winner, setWinner] = useState(null);
    const [playerColor, setPlayerColor] = useState(null); // 玩家选择的颜色
    const [hoveredCell, setHoveredCell] = useState({x: null, y: null}); // 保存鼠标悬停的位置

    const socketRef = useRef(null);
    const cellSize = 40; // 每个单元格的大小

    // WebSocket 连接与事件管理优化
    useEffect(() => {
        socketRef.current = io("http://127.0.0.1:5000");

        socketRef.current.on("connect", () => {
            console.log("Connected to Socket.IO server");
        });

        const handleGameState = (message) => {
            const {x, y, player} = message;
            handleMove(x, y, player, false); // 从服务器接收的移动不发送到服务器
        };

        const handleGameOver = (message) => {
            setWinner(message.winner);
            setGameOver(true);
        };

        socketRef.current.on("gameState", handleGameState);
        socketRef.current.on("gameOver", handleGameOver);

        socketRef.current.on("disconnect", () => {
            console.log("Disconnected from Socket.IO server");
        });

        return () => {
            socketRef.current.off("gameState", handleGameState);
            socketRef.current.off("gameOver", handleGameOver);
            socketRef.current.disconnect();
        };
    }, []);

    const handleMove = useCallback((x, y, player, sendToServer = true) => {
        if (x < 0 || x >= 15 || y < 0 || y >= 15 || !board[x]) {
            console.log("Invalid coordinates or board row undefined:", x, y);
            return;
        }
        console.log("棋盘对象: ", board); // 输出棋盘对象
        console.log("当前坐标: ", x, y); // 输出坐标
        if (!gameOver && board[x][y] === null) {
            const newBoard = board.map((row, rowIndex) =>
                row.map((cell, colIndex) => (rowIndex === x && colIndex === y ? player : cell))
            );
            setBoard(newBoard);
            setCurrentPlayer((prevPlayer) => (prevPlayer === "black" ? "white" : "black"));

            if (sendToServer) {
                socketRef.current.emit("startGame", {x, y, player});
            }

            checkWinner(newBoard, x, y, player);
        } else {
            console.log("Invalid move or game over.");
        }
    }, [board, gameOver]);


    // 检查胜利条件
    const checkWinner = useCallback((newBoard, x, y, player) => {
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
                socketRef.current.emit("gameOver", {winner: player});
                return;
            }
        }
    }, [socketRef]);

    // 鼠标移动时处理悬停的位置
    const handleMouseMove = (event) => {
        const boardRect = event.currentTarget.getBoundingClientRect();  // 使用 currentTarget
        const offsetX = event.clientX - boardRect.left;
        const offsetY = event.clientY - boardRect.top;

        const x = Math.floor(offsetX / cellSize);
        const y = Math.floor(offsetY / cellSize);

        // 输出调试信息
        console.log("Mouse Move -> OffsetX:", offsetX, "OffsetY:", offsetY);
        console.log("Calculated X:", x, "Y:", y);
        console.log("boardRect:", boardRect);
        console.log("cellSize:", cellSize);

        if (x >= 0 && x < 15 && y >= 0 && y < 15) {
            setHoveredCell({x, y});
        } else {
            setHoveredCell({x: null, y: null});
        }
    };


    const handleCellClick = useCallback(() => {
        const {x, y} = hoveredCell;
        // 输出调试信息
         console.log("x",x);
         console.log("y",y);
         console.log("Cell Click -> hoveredCell:", hoveredCell);
         console.log("Current Player:", currentPlayer);
         console.log("Player Color:", playerColor);  // 打印当前的 playerColor
        // 检查 hoveredCell 的有效性，以及玩家是否正确选择了颜色
        if (x !== null && y !== null && board[x] && board[x][y] === null && currentPlayer === playerColor) {
            handleMove(x, y, currentPlayer);
        } else {
            console.log("handleCellClick invalid");
        }
    }, [board, currentPlayer, gameOver, playerColor, hoveredCell, handleMove]);

    // 玩家选择颜色
    const handleColorSelection = (color) => {
        setPlayerColor(color);
        console.log(`Player selected ${color}`);
    };

    // 优化棋盘渲染，减少不必要的渲染
    const renderBoard = useMemo(() => {
        return (
            <div className="game-board" onMouseMove={handleMouseMove} onClick={handleCellClick}>
                {board.map((row, rowIndex) => (
                    <div key={rowIndex} className="row">
                        {row.map((cell, colIndex) => (
                            <div key={colIndex} className="cell">
                                {/* 渲染已经落下的棋子 */}
                                {cell && <div className={`piece ${cell}`}></div>}
                                {/* 显示悬停时的虚化棋子 */}
                                {hoveredCell.x === rowIndex && hoveredCell.y === colIndex && !cell && (
                                    <div className={`piece hover ${playerColor}`}></div>
                                )}
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        );
    }, [board, handleCellClick, hoveredCell, playerColor]);

    // 如果没有选择棋子颜色，显示选择颜色的界面
    if (!playerColor) {
        return (
            <div className="game-container">
                <h2>Select your color</h2>
                <button className="player-select-white-black" onClick={() => handleColorSelection("black")}>Play as
                    Black
                </button>
                <button className="player-select-white-black" onClick={() => handleColorSelection("white")}>Play as
                    White
                </button>
            </div>
        );
    }

    return (
        <div className="game-container">
            <h2>Gomoku Game</h2>
            {gameOver ? <h3>Winner: {winner}</h3> :
                <h3>Current Player: {currentPlayer === playerColor ? "You" : "Opponent"}</h3>}
            {renderBoard}
        </div>
    );
};

export default Game;
