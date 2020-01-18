#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    run the gui of private film database
    VERSION 1.0.0
    2019, Christopher Mertens
"""

from tkinter import Tk
from private_db.db_gui import DB_GUI

if __name__ == "__main__":
    root = Tk()
    db_gui = DB_GUI(root)
    root.mainloop()

