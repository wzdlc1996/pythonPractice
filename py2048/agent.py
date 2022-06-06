"""
The agent for 20488 game
"""

import numpy as np
import system as env
import random
random.seed(0)


class agent:
    def __init__(self):
        pass

    def find_act(self, state):
        """
        Find the optimal action on the given state. The output is encoded as one-hot

        :param state: (16,)-size np.array
        :return: action char, element of {"w", "s", "a", "d"}
        """

        act_char_map = {0: "w", 1: "s", 2: "a", 3: "d"}
        output_p = np.array([1, 2, 3, 4])
        act = np.argmax(output_p)
        return act_char_map[act]


def gameplay(agent, eps):
    sys = env.sys()
    done = False
    res_list = []
    while not done:
        p = random.random()
        state = sys.state().copy()
        if p < eps:
            act = random.choice(["w", "s", "a", "d"])
        else:
            act = agent.find_act(state)

        rew, done = sys.step(act)
        nstate = sys.state().copy()
        unit = {
            "curr_state": state,
            "next_state": nstate,
            "rew": rew,
            "done": done
        }
        res_list.append(unit)

    return res_list





