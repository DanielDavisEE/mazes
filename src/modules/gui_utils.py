import logging
import tkinter as tk
from tkinter import ttk


class ViewBase:
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)


class TkViewBase(ViewBase):
    frame: tk.Frame

    def init(self):
        pass


class TkGui:
    """Minimal constructor for displaying a maze with Tk"""

    def __init__(self, views: list[TkViewBase], *args, **kwargs):
        super().__init__(*args, **kwargs)

        if views is None:
            views = []

        self.root = tk.Tk()
        self.root.title("GUI")

        notebook = ttk.Notebook(self.root)

        for view in views:
            notebook.add(view.frame)
            view.init()

        # Configure window size and placement
        self.root.resizable(True, True)
        self.root.eval("tk::PlaceWindow . center")
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = TkGui()
    gui.run()
