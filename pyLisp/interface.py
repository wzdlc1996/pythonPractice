import sys
import os
import time
sys.path.append(os.path.realpath(__file__ + "/../"))

from lispker import Process

if __name__ == "__main__":
    pr = Process()
    while True:
        prog = input("lisp>")
        st = time.time()
        pr.eval(prog)
        ed = time.time()
        print(pr.result(), f"Time cost: {ed - st}s")
        # Try (Def f (x) (If (Equal x 0) 1 (Product (f (Plus x (Minus 1))) x))) for factorial!
