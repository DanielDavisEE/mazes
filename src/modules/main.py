import logging
import tkinter as tk


class MazeGui:
    """
    The controller component of the MVC gui model
    """

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

        self.root = tk.Tk()
        self.root.title("Maze GUI")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    gui = MazeGui()
    gui.run()
