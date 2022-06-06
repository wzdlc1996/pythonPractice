"""
System for reinforcement learning
"""

import game
import numpy as np


class sys:
    def __init__(self):
        self.game = game.board()
        self.state_list = [self.game.bodyFlat()]
        self.act_list = []
        self.end = False
        self.rew_list = []

    def state(self):
        return self.state_list[-1]

    def step(self, act):
        """
        simulate the game serially

        :param act: action char, element of {"w", "s", "a", "d"}
        :return rew: reward at this action
        :return done: if the game ends
        """
        changed, continu = self.game.update(act)
        self.state_list.append(self.game.bodyFlat())
        self.act_list.append(act)
        if not continu:
            done = True
            rew = game.score()
        else:
            done = False
            if not changed:
                rew = -1
            else:
                rew = 0
        self.rew_list.append(rew)
        return rew, done
