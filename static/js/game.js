document.addEventListener('DOMContentLoaded', () => {
    const gameBoard = document.getElementById('game-board');
    const resetButton = document.getElementById('reset');
    const boardSize = 15;

    // Create the board dynamically
    for (let i = 0; i < boardSize; i++) {
        for (let j = 0; j < boardSize; j++) {
            const cell = document.createElement('div');
            cell.dataset.x = i;
            cell.dataset.y = j;
            cell.addEventListener('click', handleMove);
            gameBoard.appendChild(cell);
        }
    }

    // Handle player's move
    async function handleMove(event) {
        const x = event.target.dataset.x;
        const y = event.target.dataset.y;

        try {
            const response = await fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ x: parseInt(x), y: parseInt(y) }),
            });

            const result = await response.json();

            if (result.status === 'ok') {
                event.target.classList.add('black');
                const aiMove = document.querySelector(`[data-x="${result.ai_move[0]}"][data-y="${result.ai_move[1]}"]`);
                aiMove.classList.add('white');
            } else if (result.status === 'win') {
                alert(`Player ${result.winner === 'AI' ? 'AI' : 'Human'} wins!`);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Reset the game
    resetButton.addEventListener('click', async () => {
        try {
            await fetch('/reset', { method: 'POST' });
            document.querySelectorAll('#game-board div').forEach(cell => {
                cell.classList.remove('black', 'white');
            });
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
