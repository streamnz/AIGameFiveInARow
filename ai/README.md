## AlphaZero-Gomoku (Python3 Version)

This project is a **Python 3** implementation of the AlphaZero algorithm specifically designed for playing the board game **Gomoku** (also called Gobang or Five in a Row). This repository is based on [junxiaosong's AlphaZero Gomoku](https://github.com/junxiaosong/AlphaZero_Gomoku) implementation, which I modified and upgraded to Python 3. Additionally, I extended the original code to work with a 15x15 board configuration for 5-in-a-row gameplay. The updated AI model was successfully integrated into my new project, which uses **React** for the frontend and **Python Flask** with **MySQL** for the backend.

### Key Features:
- **Python 3 Compatibility**: The original code was ported from Python 2 to Python 3, with all dependencies upgraded to support modern Python environments.
- **Custom Model for 15x15 Gomoku**: A new AI model was trained from scratch using a 15x15 board size for 5-in-a-row.
- **AI Integration**: The trained model was incorporated into my full-stack project, where the frontend uses React, and the backend is built with Python Flask and MySQL.

### References:
1. AlphaZero: Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
2. AlphaGo Zero: Mastering the game of Go without human knowledge

### Example Game Between Trained Models
- The AI model, trained with 400 MCTS playouts, playing on a 15x15 board with 5-in-a-row rules.

### Requirements
The project has the following requirements:
- **Python >= 3.7**
- **Numpy >= 1.18**
- **PyTorch >= 1.4** (For training AI models)
- **Flask >= 1.1.2** (For backend development)
- **MySQL** (For database integration with the backend)

To train the AI model from scratch:
- PyTorch >= 1.4 is recommended, but you can also use TensorFlow if you modify the `policy_value_net` file.

### Getting Started

#### To play against the AI with the pre-trained model:
Run the following script from the directory:

```bash
python human_play.py
```

#### To train the AI model from scratch:
Run the following script from the directory:

```bash
python train.py
```

#### To play against the AI with the trained model:
Run the following script from the directory:

```bash
python
```
You can modify human_play.py to test different configurations or models.
To train the AI model from scratch:  
Run the following script from the directory:

```bash
python train.py
```
Important Notes for Training:
To train the AI model from scratch:
Edit the train.py script to choose the correct framework for training:

Uncomment the following line for PyTorch:

```python
# net = PolicyValueNet(board_width, board_height, model_file=None)
```

Uncomment the following line for TensorFlow:

```python
# net = PolicyValueNetNumpy(board_width, board_height, model_file=None)
```

The models (best_policy.model and current_policy.model) will be saved periodically during training (default is every 50 updates).

### Important Notes for PyTorch Training:
- To use **GPU** with PyTorch, make sure `use_gpu=True` in `train.py` and ensure you have a CUDA-enabled GPU with the appropriate drivers.
- If using PyTorch version >0.5, modify the `train_step` function in `policy_value_net_pytorch.py` to use `loss.item()` and `entropy.item()` as return values.

### AI Model Integration in Full-Stack Project:
In my new full-stack project:

- **Frontend**: The game UI is implemented using **React**.
- **Backend**: The backend, built with **Flask**, handles requests for game data and manages AI moves through the trained model. The backend also integrates with **MySQL** for storing game results, user data, and AI performance metrics.
- The previously implemented AI logic in the backend has been replaced by the newly trained 15x15 AlphaZero-based AI model.

### Model Training Tips:
- **Smaller Boards**: Starting with a smaller 6x6 board and 4-in-a-row rules can give you a working model quickly (within 500~1000 self-play games). This takes around 2 hours on a single PC.
- **Larger Boards**: For a 15x15 board with 5-in-a-row, you may need 2000~3000 self-play games to get a good model, which may take a couple of days depending on your machine.

### Further Reading:
Original article by the creator of the base version (in Chinese): [https://zhuanlan.zhihu.com/p/32089487](https://zhuanlan.zhihu.com/p/32089487)
