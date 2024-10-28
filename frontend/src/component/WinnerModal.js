import React, { useEffect, useState } from "react";
import "animate.css"; // 引入 animate.css
import Confetti from 'react-confetti'; // 撒花效果
import "./WinnerModal.css"; // 引入 WinnerModal.css

// 增加了 playerColor 参数
const WinnerModal = ({ winner, playerColor, onClose }) => {
    const [userName, setUserName] = useState('');
    const [isWinner, setIsWinner] = useState(false);

    useEffect(() => {
        const storedUserName = localStorage.getItem('username') || 'Player';
        setUserName(storedUserName);

        // 判断当前玩家是否是获胜方
        if (playerColor === winner) {
            setIsWinner(true);
        }
    }, [winner, playerColor]);

    return (
        <div className="winner_modal-overlay">
            {isWinner && <Confetti />} {/* 只在获胜时撒花 */}
            <div className="winner_modal-content animate__animated animate__zoomIn"> {/* 使用 animate.css 的 zoomIn 动画 */}
                <h2>Game Over</h2>
                <p className="animate__animated animate__fadeInUp animate__delay-1s">
                    {isWinner ? (
                        <>
                            🎉 <strong>Kua wikitoria koe, {userName}!</strong> 🎉
                            <br />
                            You, as the <strong>{winner}</strong> side, won the game!
                        </>
                    ) : (
                        <>
                            😔 <strong>Aroha mai, {userName}!</strong>
                            <br />
                            You, as the <strong>{playerColor}</strong> side, lost the game to the <strong>{winner}</strong> side.
                        </>
                    )}
                </p>
                <button onClick={onClose} className="animate__animated animate__bounceIn animate__delay-2s">
                    Close
                </button>
            </div>
        </div>
    );
};

export default WinnerModal;
