
# Ronald Du
# from tkinter import *
# from tkinter.ttk import *

# from cefpython3 import cefpython as cef

from cefpython3 import cefpython as cef
import ctypes
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import sys
import os
import platform
import logging as _logging


MainWindow = Tk()

MainWindow.title("NetDiscover")

MainWindow.mainloop()