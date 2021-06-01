import game
import tkinter as tk


class gameui(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title = "2048"
        self.master.geometry("600x600+200+50")
        self.game = game.board()
        self.game.setRandBox()

        marg = 25
        box_size = 100
        font_size = 20
        board_wid = 2
        canv_size = 4 * box_size + 3 * marg

        self.canv = tk.Canvas(
            self.master,
            width=canv_size + board_wid,
            height=canv_size + board_wid + box_size/2
        )
        self.canv.pack()

        x = board_wid
        y = board_wid + box_size/2
        self.box = {}

        # Create boxes in the canvas and store the text_id in self.box
        for i in range(4):
            for j in range(4):
                self.canv.create_rectangle(x, y, x + box_size, y + box_size)
                self.box[(i, j)] = self.canv.create_text(
                    x + box_size / 2, y + box_size / 2, text=self.game[(i, j)],
                    font=("Arial", font_size)
                )
                x += box_size + marg
            x = board_wid
            y += box_size + marg

        def upd(event):
            ch, cont = self.game.update(event.char)
            if cont:
                self.sync()
            else:
                self.fin()

        self.master.bind("<Key>", upd)

    def sync(self):
        """
        sync the game body and front-end rendering

        :return:
        """
        for _, ((i, j), b) in enumerate(self.box.items()):
            self.canv.itemconfigure(b, text=self.game[i, j])

    def fin(self):
        """
        game finish

        :return:
        """
        fl, score = self.game.status()
        tk.Message("End with score: {}".format(score))



if __name__ == "__main__":
    root = tk.Tk()
    main = gameui(root)
    main.mainloop()