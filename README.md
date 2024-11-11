# FiveChessWithAI (Gomoku with AI)

This is a web-based implementation of the classic **Gomoku (Five in a Row)** game with an AI opponent. The project is built using **Flask** for the backend and supports user login, AI gameplay, and a leaderboard to track players' scores. The AI is implemented using algorithms like Minimax with Alpha-Beta pruning.

## Project Structure
`````
FiveChessWithAI/
├── ai/
│   ├── game.py                  # Defines Board and Game classes for Gomoku
│   ├── human_play.py            # Implements human vs AI gameplay
│   ├── mcts_alphaZero.py        # Monte Carlo Tree Search for AlphaZero
│   ├── policy_value_net_pytorch.py # PyTorch implementation of policy-value network
│   ├── train.py                 # Training pipeline for AlphaZero
│   └── README.md                # Documentation for AI implementation
├── app.py                       # Flask application main entry point
├── config.py                    # Application configuration
├── controller/
│   ├── game_controller.py       # Handles game-related routes and logic
│   └── user_controller.py       # Handles user authentication and leaderboard
├── dao/
│   ├── game_dao.py              # Database access for game state
│   └── user_dao.py              # Database access for user management
├── model/
│   └── user.py                  # User model for authentication
├── service/
│   ├── game_service.py          # Business logic for the game
│   └── user_service.py          # Logic for managing users and authentication
├── source/
│   ├── AI.py                    # AI logic (Minimax with Alpha-Beta pruning)
│   ├── gomoku.py                # Game state management
│   └── utils.py                 # Helper functions for the game
├── static/                      # Static files (CSS, images, JavaScript)
├── templates/                   # HTML templates
├── utils/
│   ├── config.ini               # Configuration file
│   └── jwt_util.py              # JWT utility functions
├── websocket/
│   └── MyWebsocket.py           # WebSocket implementation for real-time gameplay
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
`````
## Features

1. **Gomoku Gameplay**: Play the classic Five-in-a-Row game.
2. **AI Opponent**: The AI opponent is built using Minimax and Alpha-Beta pruning.
3. **User Login & Registration**: Players can register and log in to track their scores.
4. **Leaderboard**: Players who beat the AI are added to a leaderboard, which displays on the game page.
5. **Responsive Frontend**: Game board, login form, and leaderboard are all rendered using HTML, CSS, and JavaScript.

## How to Run

1. **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/FiveChessWithAI.git
    cd FiveChessWithAI
    ```

2. **Set up the Python virtual environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database**:

    You will need to initialize the SQLite database by running:

    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. **Run the Flask application**:

    ```bash
    flask run
    ```

6. **Access the application**:

    Open a browser and navigate to `http://127.0.0.1:5000` to access the game and login page.

## Project Dependencies

The `requirements.txt` file includes all the Python dependencies required for this project. The key libraries used are:

- **Flask**: Backend framework for handling HTTP requests.
- **Flask-SQLAlchemy**: SQLAlchemy for handling the SQLite database.
- **Flask-Migrate**: For handling database migrations.
- **WTForms & Flask-WTF**: For user registration and login form validation.
- **Matplotlib & Pandas**: Used for evaluating AI performance (optional).

## Screenshots

- **Login Page**:
    ![Login Page](static/images/login_screenshot.png)
- **Game Board**:
    ![Game Board](static/images/game_board_screenshot.png)

## Future Improvements

- Improve the AI by using more advanced algorithms or neural networks.
- Add multiplayer support.
- Add more game features like timers, chat, and difficulty levels.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
