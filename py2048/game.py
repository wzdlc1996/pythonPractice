import numpy as np

class board:
    def __init__(self):
        self.body = np.zeros((4, 4), dtype=int)

    def status(self):
        return len(self.getEmpty()) == 0, 2 ** np.max(self.body)

    def getEmpty(self):
        return np.argwhere(self.body == 0)

    def setRandBox(self):
        emptyBoxes = self.getEmpty()
        ind = np.random.choice(np.arange(len(emptyBoxes)))
        self.body[tuple(emptyBoxes[ind])] = 1

    def merge(self) -> bool:
        """
        Merge along the left direction

        :param self:
        :return: whether the board is changed or not
        """
        changed = False
        for i in range(4):
            items = self.body[i, :]
            nums = items[np.nonzero(items)]
            for j in range(len(nums) - 1):
                if nums[j] == nums[j+1]:
                    changed = True
                    nums[j] += 1
                    nums[j+1] = 0
            nums = nums[np.nonzero(nums)]
            self.body[i, :] = np.append(nums, np.zeros(4 - len(nums)))

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

        self.setRandBox()

        return changed

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

