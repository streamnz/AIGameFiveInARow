import React from "react";

const WinnerModal = ({ winner, onClose }) => {
    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Game Over</h2>
                <p>The winner is: <strong>{winner}</strong></p>
                <button onClick={onClose}>Close</button>
            </div>
        </div>
    );
};

export default WinnerModal;
