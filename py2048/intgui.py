import game
import tkinter as tk
import time


class gameui(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title = "2048"
        self.master.geometry("600x600+200+50")
        self.game = game.board()
        self.game.setRandBox()
        self.canv = tk.Canvas(
            self.master,
            width=475+2,
            height=475+2+50
        )
        self.canv.pack()
        x = 2
        y = 2 + 50
        self.box = {}
        for i in range(4):
            for j in range(4):
                self.canv.create_rectangle(x, y, x + 100, y + 100)
                self.box[(i, j)] = self.canv.create_text(
                    x + 50, y + 50, text=self.game[(i, j)],
                    font=("Arial", 20)
                )
                x += 125
            x = 2
            y += 125

        def upd(event):
            ch, cont = self.game.update(event.char)
            if cont:
                self.sync()
            else:
                self.fin()

        self.master.bind("<Key>", upd)

    def sync(self):
        for _, ((i, j), b) in enumerate(self.box.items()):
            self.canv.itemconfigure(b, text=self.game[i, j])

    def fin(self):
        fl, score = self.game.status()
        tk.Message("End with score: {}".format(score))



if __name__ == "__main__":
    root = tk.Tk()
    main = gameui(root)
    main.mainloop()