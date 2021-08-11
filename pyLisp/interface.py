import sys
import os
sys.path.append(os.path.realpath(__file__ + "/../"))

from lispker import Process

if __name__ == "__main__":
    pr = Process()
    while True:
        prog = input("lisp>")
        pr.eval(prog)
        print(pr.result())
