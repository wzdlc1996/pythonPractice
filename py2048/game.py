import numpy as np


class board:
    def __init__(self):
        self.body = np.zeros((4, 4), dtype=int)

    def __getitem__(self, slc):
        x = self.body[slc]
        if x == 0:
            tex = ""
        else:
            tex = str(2 ** x)
        return tex

    def status(self):
        return len(self.getEmpty()) == 0, 2 ** np.max(self.body)

    def getEmpty(self):
        return np.argwhere(self.body == 0)

    def setRandBox(self):
        emptyBoxes = self.getEmpty()
        try:
            ind = np.random.choice(np.arange(len(emptyBoxes)))
            self.body[tuple(emptyBoxes[ind])] = 1
            return True
        except ValueError:
            return False


    def merge(self) -> bool:
        """
        Merge along the left direction

        :param self:
        :return: whether the board is changed or not
        """
        changed = False
        for i in range(4):
            items = self.body[i, :]
            back = items.copy()
            nums = items[np.nonzero(items)]
            for j in range(len(nums) - 1):
                if nums[j] == nums[j+1]:
                    nums[j] += 1
                    nums[j+1] = 0
            nums = nums[np.nonzero(nums)]
            res = np.append(nums, np.zeros(4 - len(nums)))
            self.body[i, :] = res
            changed = changed or (not ((res == back).all()))
        return changed

    def rever(self):
        self.body = self.body[:, ::-1]

    def trans(self):
        self.body = np.transpose(self.body)

    def update(self, move):
        """
        Update the board according to the move

        :param move: element of {"w", "a", "s", "d"}
        :return: whether the board is changed or not
        """
        if move == "a":
            changed = self.merge()

        elif move == "d":
            self.rever()
            changed = self.merge()
            self.rever()

        elif move == "w":
            self.trans()
            changed = self.merge()
            self.trans()

        elif move == "s":
            self.trans()
            self.rever()
            changed = self.merge()
            self.rever()
            self.trans()

        else:
            raise ValueError("Invalid movement")

        res = True
        if changed:
            res = self.setRandBox()

        return changed, res

    def __str__(self):
        return "\n".join(["\t".join([str(y) for y in x]) for x in self.body])


if __name__ == "__main__":
    game = board()
    game.setRandBox()
    print(game)
    while True:
        end, score = game.status()
        if end:
            print("Game end, your score is {}".format(score))
            exit(0)
        move = input("(w, s, a, d) to move, (e) to exit:")
        if move == "e":
            exit(0)
        game.update(move)
        print(game)

