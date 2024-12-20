# -*- coding: utf-8 -*-
"""
An implementation of the training pipeline of AlphaZero for Gomoku

@author: Junxiao Song
@Modify Hao Cheng
"""

import random
import numpy as np
from collections import defaultdict, deque
import torch
from ai.game import Board, Game
from ai.mcts_pure import MCTSPlayer as MCTS_Pure
from ai.mcts_alphaZero import MCTSPlayer
from ai.policy_value_net_pytorch import PolicyValueNet  # 使用 PyTorch 版的 PolicyValueNet
import time


class TrainPipeline():
    def __init__(self, init_model=None):
        # params of the board and the game
        self.board_width = 15  # 修改成你的具体需求
        self.board_height = 15  # 修改成你的具体需求
        self.n_in_row = 5  # 修改成你的具体需求
        self.board = Board(width=self.board_width,
                           height=self.board_height,
                           n_in_row=self.n_in_row)
        self.game = Game(self.board)
        # training params
        self.learn_rate = 1e-3
        self.lr_multiplier = 1.0  # adaptively adjust the learning rate based on KL
        self.temp = 1.0  # the temperature param
        self.n_playout = 800  # num of simulations for each move
        self.c_puct = 5
        self.buffer_size = 10000
        self.batch_size = 1024  # mini-batch size for training
        self.data_buffer = deque(maxlen=self.buffer_size)
        self.play_batch_size = 1
        self.epochs = 10  # num of train_steps for each update
        self.kl_targ = 0.05
        self.check_freq = 50
        self.game_batch_num = 1500
        self.best_win_ratio = 0.0
        # num of simulations used for the pure mcts, which is used as
        # the opponent to evaluate the trained policy
        self.pure_mcts_playout_num = 1000

        # 根据棋盘长宽和n_in_row动态生成模型文件名
        self.model_filename = f'best_policy_{self.board_width}_{self.board_height}_{self.n_in_row}.model2'

        if init_model:
            self.policy_value_net = PolicyValueNet(self.board_width,
                                                   self.board_height,
                                                   model_file=init_model)
        else:
            self.policy_value_net = PolicyValueNet(self.board_width,
                                                   self.board_height)
        self.mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn,
                                      c_puct=self.c_puct,
                                      n_playout=self.n_playout,
                                      is_selfplay=1)
        self.start_time = time.time()  # 记录训练开始时间

    def get_equi_data(self, play_data):
        """augment the data set by rotation and flipping"""
        extend_data = []
        for state, mcts_prob, winner in play_data:
            for i in [1, 2, 3, 4]:
                equi_state = np.array([np.rot90(s, i) for s in state])
                equi_mcts_prob = np.rot90(np.flipud(
                    mcts_prob.reshape(self.board_height, self.board_width)), i)
                extend_data.append((equi_state,
                                    np.flipud(equi_mcts_prob).flatten(),
                                    winner))
                equi_state = np.array([np.fliplr(s) for s in equi_state])
                equi_mcts_prob = np.fliplr(equi_mcts_prob)
                extend_data.append((equi_state,
                                    np.flipud(equi_mcts_prob).flatten(),
                                    winner))
        return extend_data

    def collect_selfplay_data(self, n_games=1):
        """collect self-play data for training"""
        for i in range(n_games):
            winner, play_data = self.game.start_self_play(self.mcts_player, temp=self.temp)
            play_data = list(play_data)[:]
            self.episode_len = len(play_data)
            play_data = self.get_equi_data(play_data)
            self.data_buffer.extend(play_data)

    def policy_update(self):
        """update the policy-value net"""
        mini_batch = random.sample(self.data_buffer, self.batch_size)
        state_batch = np.array([data[0] for data in mini_batch], dtype=np.float32)
        mcts_probs_batch = np.array([data[1] for data in mini_batch], dtype=np.float32)
        winner_batch = np.array([data[2] for data in mini_batch], dtype=np.float32)

        state_batch = torch.FloatTensor(state_batch)
        mcts_probs_batch = torch.FloatTensor(mcts_probs_batch)
        winner_batch = torch.FloatTensor(winner_batch)

        old_probs, old_v = self.policy_value_net.policy_value(state_batch)

        for i in range(self.epochs):
            loss, entropy = self.policy_value_net.train_step(
                state_batch, mcts_probs_batch, winner_batch,
                self.learn_rate * self.lr_multiplier)
            new_probs, new_v = self.policy_value_net.policy_value(state_batch)

            kl = np.mean(np.sum(old_probs * (
                    np.log(old_probs + 1e-10) - np.log(new_probs + 1e-10)), axis=1))
            if kl > self.kl_targ * 4:  # early stopping if D_KL diverges badly
                break

        # adaptively adjust the learning rate
        if kl > self.kl_targ * 2 and self.lr_multiplier > 0.1:
            self.lr_multiplier /= 1.5
        elif kl < self.kl_targ / 2 and self.lr_multiplier < 10:
            self.lr_multiplier *= 1.5

        explained_var_old = (1 - np.var(np.array(winner_batch) - old_v.flatten()) /
                             np.var(np.array(winner_batch)))
        explained_var_new = (1 - np.var(np.array(winner_batch) - new_v.flatten()) /
                             np.var(np.array(winner_batch)))

        print(f"KL divergence: {kl:.5f}, lr_multiplier: {self.lr_multiplier:.3f}, "
              f"loss: {loss:.5f}, entropy: {entropy:.5f}, "
              f"explained_var_old: {explained_var_old:.5f}, explained_var_new: {explained_var_new:.5f}")

        return loss, entropy

    def policy_evaluate(self, n_games=10):
        """Evaluate the trained policy by playing against the pure MCTS player"""
        current_mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn, c_puct=self.c_puct,
                                         n_playout=self.n_playout)
        pure_mcts_player = MCTS_Pure(c_puct=5, n_playout=self.pure_mcts_playout_num)
        win_cnt = defaultdict(int)

        for i in range(n_games):
            winner = self.game.start_play(current_mcts_player, pure_mcts_player, start_player=i % 2, is_shown=0)
            win_cnt[winner] += 1

        win_ratio = 1.0 * (win_cnt[1] + 0.5 * win_cnt[-1]) / n_games
        print(f"Win ratio: {win_ratio:.2f}, wins: {win_cnt[1]}, losses: {win_cnt[2]}, ties: {win_cnt[-1]}")

        return win_ratio

    def run(self):
        """run the training pipeline"""
        try:
            for i in range(self.game_batch_num):
                start_time = time.time()  # 开始时间
                self.collect_selfplay_data(self.play_batch_size)

                if len(self.data_buffer) > self.batch_size:
                    loss, entropy = self.policy_update()

                if (i + 1) % self.check_freq == 0:
                    win_ratio = self.policy_evaluate()

                    # 保存当前模型
                    self.policy_value_net.save_model(
                        f'./current_policy_{self.board_width}_{self.board_height}_{self.n_in_row}.model2')

                    # 保存最佳模型
                    if win_ratio > self.best_win_ratio:
                        print(f"New best policy at batch {i + 1}")
                        self.best_win_ratio = win_ratio
                        self.policy_value_net.save_model(f'./{self.model_filename}')
                        if self.best_win_ratio == 1.0 and self.pure_mcts_playout_num < 5000:
                            self.pure_mcts_playout_num += 1000
                            self.best_win_ratio = 0.0

                end_time = time.time()  # 结束时间
                batch_time = end_time - start_time
                remaining_batches = self.game_batch_num - (i + 1)
                remaining_time = remaining_batches * batch_time

                print(f"Batch {i + 1}/{self.game_batch_num} completed in {batch_time:.2f} seconds.")
                print(
                    f"Estimated remaining time: {remaining_time // 60:.0f} minutes {remaining_time % 60:.0f} seconds.")

        except KeyboardInterrupt:
            print("Training interrupted.")


if __name__ == '__main__':
    training_pipeline = TrainPipeline()
    training_pipeline.run()
