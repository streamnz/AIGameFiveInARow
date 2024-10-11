# -*- coding: utf-8 -*-
"""
human VS AI models
Input your move in the format: 2,3
@author: Junxiao Song
@Modify Hao Cheng
"""

import torch
from game import Board, Game
from mcts_pure import MCTSPlayer as MCTS_Pure
from mcts_alphaZero import MCTSPlayer
from policy_value_net_pytorch import PolicyValueNet  # Pytorch

class Human(object):
    """
    human player
    """

    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        try:
            location = input("Your move: ")
            if isinstance(location, str):  # for python3
                location = [int(n) for n in location.split(",")]
            move = board.location_to_move(location)
        except Exception as e:
            print(f"Error in move input: {e}")
            move = -1
        if move == -1 or move not in board.availables:
            print("Invalid move. Try again.")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)


def run():
    n = 5
    width, height = 8, 8
    model_file = 'current_policy_8_8_5.model2'
    try:
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)

        # ############### human VS AI ###################
        # load the trained policy_value_net from PyTorch
        # If you trained a model and saved it as `best_policy_8_8_5.model`
        best_policy = PolicyValueNet(width, height, model_file=model_file, use_gpu=torch.cuda.is_available())

        mcts_player = MCTSPlayer(best_policy.policy_value_fn,
                                 c_puct=5,
                                 n_playout=400)  # set larger n_playout for better performance

        # uncomment the following line to play with pure MCTS (it's much weaker even with a larger n_playout)
        # mcts_player = MCTS_Pure(c_puct=5, n_playout=1000)

        # human player, input your move in the format: 2,3
        human = Human()

        # set start_player=0 for human first
        game.start_play(human, mcts_player, start_player=1, is_shown=1)

    except KeyboardInterrupt:
        print('\nGame interrupted. Exiting.')


if __name__ == '__main__':
    run()
