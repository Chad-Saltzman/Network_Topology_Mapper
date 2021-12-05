
# Ronald Du

# Tkinter Front End

# not upscaling to 4k right. is this a 4K problem??

# this only runs with Python 3.9 and lower on Windows!
# on Linux and Mac, CEFPython3 currently only supports up to Python 3.7!!!

# do not try to drag the window on demo day... it will crash

# lets us run C code and call DLLs in Windows
import ctypes
# imports tkinter for the basic gui
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    from Tkinter import filedialog

# imports basic libaries needed
import sys
import os
import platform


# for grabbing current path
import pathlib

# for running the graph html file
from cefpython3 import cefpython as cef

# logging library for debugging
import logging as _logging


WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

logger = _logging.getLogger("tkinter_.py")

IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"


def main():

    root = tk.Tk()
    root.iconbitmap('NetDiscover_Logo.ico')
    
    if WINDOWS:
        # this sets the window icon of the main windoww

        # root.iconbitmap(default='NetDiscover_Logo.ico')
        # sets the application ID

        NetDiscoverAppID = u'CS425.Team14.NetDiscover.Prototype'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            NetDiscoverAppID)
        # make the program multi threaded
        # print("Is this even running??")
        # yeah it is
        settings = {'multi_threaded_message_loop': True}
        # fixes ugly 4k scaling on my 4k monitors
        # ctypes.windll.shcore.SetProcessDpiAwareness(True)

    app = MainFrame(root)
    # canvas1 = tk.Frame(root, width=600, height=300, bg='yellow')

    # default settings for CEF (linux?) will be default
    settings = {}

    # if this program is running on windows, set the taskbar icon to this
    # also assigns this application an app ID for Windows

    # if program is running on MAC, needs external messgae pump
    if MAC:
        settings["external_message_pump"] = True

    # intializes the chronium window
    cef.Initialize(settings=settings)

    # print(pathlib.Path().absolute())

    app.mainloop()
    logger.debug("Main loop exited")
    cef.Shutdown()


#main window
class MainFrame(tk.Frame):

    def __init__(self, root):

        # creates the menubar

        self.browser_frame = None
        self.navigation_bar = None
        # self.SideButtons = None

        # self.ViewPanel = None

        self.root = root


        # Root
        # this sets the resolution of the new window
        # YScaledRes = self.scaled(1450)
        # XScaledRes = self.scaled(900)
        # root.geometry(str(self.scaled(1450))+'x'+str(self.scaled(900)))

        root.geometry("1450x700")

        # root.iconphoto(False, tk.PhotoImage(file='NetDiscover_Logo.png'))
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=1)

        menubar = tk.Menu(self.root, tearoff=0)
        # cpane = CollapsiblePane(root, 'Expanded', 'Collapsed')
        root.tk.call('wm', 'iconphoto', root._w,
                     tk.PhotoImage(file='NetDiscover_Logo.png'))
        self.root.config(menu=menubar)

        # This creates a new File Menu
        FileMenu = tk.Menu(menubar, tearoff=0)
        FileMenu.add_command(label="Open", command=self.OpenFileExplorer)
        FileMenu.add_command(label="Save", command=self.SaveFileExplorer)
        FileMenu.add_command(label="WhoKnows", command=self.onExit)
        menubar.add_cascade(label="File", menu=FileMenu)

        # Creates a new Edit Menu
        EditMenu = tk.Menu(menubar, tearoff=0)
        EditMenu.add_command(label="Add", command=self.onExit)
        EditMenu.add_command(label="Delete", command=self.onExit)
        EditMenu.add_command(label="WhoKnows", command=self.onExit)
        menubar.add_cascade(label="Edit", menu=EditMenu)

        # what exactly do we need?
        NodeMenu = tk.Menu(menubar, tearoff=0)
        NodeMenu.add_command(label="Add Node", command=self.onExit)
        NodeMenu.add_command(label="Delete Node", command=self.onExit)
        NodeMenu.add_command(label="Examine Node", command=self.onExit)
        menubar.add_cascade(label="Node", menu=NodeMenu)

        # what exactly do we need?
        AnalysisMenu = tk.Menu(menubar, tearoff=0)
        AnalysisMenu.add_command(label="???", command=self.onExit)
        AnalysisMenu.add_command(label="???", command=self.onExit)
        AnalysisMenu.add_command(label="???", command=self.onExit)
        menubar.add_cascade(label="Analysis", menu=AnalysisMenu)


        
        # this is supposed to be a side panel
        # no longer object oriented after this
        ViewPanel = tk.Frame(root, width=200, bg='white', height=500, relief='sunken', borderwidth=2)
        ViewPanel.pack(expand=False, fill='y', side='left', anchor='nw')

        # MainFrame
        tk.Frame.__init__(self, root)
        self.master.title("NetDiscover")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Configure>", self.on_root_configure)

        self.bind("<Configure>", self.on_configure)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        # NavigationBar
        self.navigation_bar = NavigationBar(self)
        self.navigation_bar.grid(row=0, column=0,
                                sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 0, weight=0)
        tk.Grid.columnconfigure(self, 0, weight=0)

        # BrowserFrame
        self.browser_frame = BrowserFrame(self, self.navigation_bar)
        self.browser_frame.grid(row=1, column=0,
                                sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        # Pack MainFrame
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def on_root_configure(self, _):
        logger.debug("MainFrame.on_root_configure")
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        logger.debug("MainFrame.on_configure")
        # is this what sets it???
        if self.browser_frame:
            width = event.width
            height = event.height
            if self.navigation_bar:
                height = height - self.navigation_bar.winfo_height()
            self.browser_frame.on_mainframe_configure(width, height)

    def on_focus_in(self, _):
        logger.debug("MainFrame.on_focus_in")

    def on_focus_out(self, _):
        logger.debug("MainFrame.on_focus_out")

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
            self.browser_frame = None
        else:
            self.master.destroy()

    # def scaled(self, original_res):
    #     screen = tk.Tk()
    #     current_dpi = screen.winfo_fpixels('1i')
    #     screen.destroy()

    #     SCALE = current_dpi/20
    #     return round(original_res * SCALE)

    # need to make the program DPI aware cause it looks really bad on my screens with high DPI

    # this function "opens" up a file and saves it to filename variable
    # this function should call a bunch of other functions that let it open something

    def OpenFileExplorer(self):
        filename = tk.filedialog.askopenfile()
        print(filename)

    # this function should "save" a file and assigns wherevere it dumped it to filename variable
    # this function should call a bunch of other functions that let it savesomething

    def SaveFileExplorer(self):
        filename = tk.filedialog.askopenfile()
        print(filename)

    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None

    # when this is called exit the program
    def onExit(self):
        self.quit()

#is
class BrowserFrame(tk.Frame):

    def __init__(self, mainframe, navigation_bar=None):
        self.navigation_bar = navigation_bar
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, mainframe)
        self.mainframe = mainframe
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        """For focus problems see Issue #255 and Issue #535. """
        self.focus_set()

    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        # self.browser = cef.CreateBrowserSync(window_info, url="file:///C:/Users/duron/Desktop/Network_Topology_Mapper-RonaldToolbarsButtons/nx.html")
        # will now work from anywhere as long as the html file is named nx.html is in the same directory
        self.browser = cef.CreateBrowserSync(
            window_info, url="file://" + str(pathlib.Path().absolute()) + "/nx.html")
        assert self.browser
        self.browser.SetClientHandler(LifespanHandler(self))
        self.browser.SetClientHandler(LoadHandler(self))
        # self.browser.SetClientHandler(FocusHandler(self))
        self.message_loop_work()

    def get_window_handle(self):
        if MAC:
            # Do not use self.winfo_id() on Mac, because of these issues:
            # 1. Window id sometimes has an invalid negative value (Issue #308).
            # 2. Even with valid window id it crashes during the call to NSView.setAutoresizingMask:
            #    https://github.com/cztomczak/cefpython/issues/309#issuecom t-661094466
            #
            # To fix it using PyObjC package to obtain window handle. If you change structure of windows then you
            # need to do modifications here as well.
            #
            # There is still one issue with this solution. Sometimes there is more than one window, for example when application
            # didn't close cleanly last time Python displays an NSAlert window asking whether to Reopen that window. In such
            # case app will crash and you will see in console:
            # > Fatal Python error: PyEval_RestoreThread: NULL tstate
            # > zsh: abort      python tkinter_.py
            # Error messages related to this: https://github.com/cztomczak/cefpython/issues/441
            #
            # There is yet another issue that might be related as well:
            # https://github.com/cztomczak/cefpython/issues/583

            # noinspection PyUnresolvedReferences
            from AppKit import NSApp
            # noinspection PyUnresolvedReferences
            import objc
            logger.info("winfo_id={}".format(self.winfo_id()))
            # noinspection PyUnresolvedReferences
            content_view = objc.pyobjc_id(NSApp.windows()[-1].contentView())
            logger.info("content_view={}".format(content_view))
            return content_view
        elif self.winfo_id() > 0:
            return self.winfo_id()
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if WINDOWS:
                # all this does is change the location of the window ???
                print("blah blh blah")
                # ???
                # this must auto resize it somehow
                ctypes.windll.user32.SetWindowPos(
                    self.browser.GetWindowHandle(), 0, 0, 0, width, height, 0)
            elif LINUX:
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        logger.debug("BrowserFrame.on_focus_in")
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        logger.debug("BrowserFrame.on_focus_out")
        """For focus problems see Issue #255 and Issue #535. """
        if LINUX and self.browser:
            self.browser.SetFocus(False)

    def on_root_close(self):
        logger.info("BrowserFrame.on_root_close")
        if self.browser:
            logger.debug("CloseBrowser")
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        else:
            logger.debug("tk.Frame.destroy")
            self.destroy()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.browser = None


class LifespanHandler(object):

    def __init__(self, tkFrame):
        self.tkFrame = tkFrame

    def OnBeforeClose(self, browser, **_):
        logger.debug("LifespanHandler.OnBeforeClose")
        self.tkFrame.quit()


class LoadHandler(object):

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    # def OnLoadStart(self, browser, **_):
    #     if self.browser_frame.master.navigation_bar:
    #         self.browser_frame.master.navigation_bar.set_url(browser.GetUrl())


class NavigationBar(tk.Frame):

    def __init__(self, master):

        self.back_state = tk.NONE
        self.forward_state = tk.NONE
        self.back_image = None
        self.forward_image = None
        self.reload_image = None

        tk.Frame.__init__(self, master)
        resources = os.path.join(os.path.dirname(__file__), "resources")

        # # Back button
        # back_png = os.path.join(resources, "back"+IMAGE_EXT)
        # if os.path.exists(back_png):
        #     self.back_image = tk.PhotoImage(file=back_png)
        # self.back_button = tk.Button(self, image=self.back_image,
        #                              command=self.go_back)

        # # self.back_button = tk.Menu(self)
        # self.back_button.grid(row=0, column=0)

        # # Forward button
        # forward_png = os.path.join(resources, "forward"+IMAGE_EXT)
        # if os.path.exists(forward_png):
        #     self.forward_image = tk.PhotoImage(file=forward_png)
        # self.forward_button = tk.Button(self, image=self.forward_image,
        #                                 command=self.go_forward)
        # self.forward_button.grid(row=0, column=1)

        # Reload button
        reload_png = os.path.join(resources, "reload"+IMAGE_EXT)
        if os.path.exists(reload_png):
            self.reload_image = tk.PhotoImage(file=reload_png)
        self.reload_button = tk.Button(self, image=self.reload_image,
                                       command=self.reload)
        self.reload_button.grid(row=0, column=2)

        # # Url entry
        # self.url_entry = tk.Entry(self)
        # self.url_entry.bind("<FocusIn>", self.on_url_focus_in)
        # self.url_entry.bind("<FocusOut>", self.on_url_focus_out)
        # self.url_entry.bind("<Return>", self.on_load_url)
        # self.url_entry.bind("<Button-1>", self.on_button1)
        # self.url_entry.grid(row=0, column=3,
        #                     sticky=(tk.N + tk.S + tk.E + tk.W))
        # tk.Grid.rowconfigure(self, 0, weight=100)
        # tk.Grid.columnconfigure(self, 3, weight=100)

        # Update state of buttons
        # self.update_state()

    # def go_back(self):
    #     if self.master.get_browser():
    #         self.master.get_browser().GoBack()

    # def go_forward(self):
    #     if self.master.get_browser():
    #         self.master.get_browser().GoForward()

    def reload(self):
        if self.master.get_browser():
            self.master.get_browser().Reload()

    # def set_url(self, url):
    #     self.url_entry.delete(0, tk.END)
    #     self.url_entry.insert(0, url)

    # def on_url_focus_in(self, _):
    #     logger.debug("NavigationBar.on_url_focus_in")

    # def on_url_focus_out(self, _):
    #     logger.debug("NavigationBar.on_url_focus_out")

    def on_load_url(self, _):
        if self.master.get_browser():
            self.master.get_browser().StopLoad()
            self.master.get_browser().LoadUrl(self.url_entry.get())

    def on_button1(self, _):
        """For focus problems see Issue #255 and Issue #535. """
        logger.debug("NavigationBar.on_button1")
        self.master.master.focus_force()

    # def update_state(self):
    #     browser = self.master.get_browser()
    #     if not browser:
    #         if self.back_state != tk.DISABLED:
    #             self.back_button.config(state=tk.DISABLED)
    #             self.back_state = tk.DISABLED
    #         if self.forward_state != tk.DISABLED:
    #             self.forward_button.config(state=tk.DISABLED)
    #             self.forward_state = tk.DISABLED
    #         self.after(100, self.update_state)
    #         return
    #     if browser.CanGoBack():
    #         if self.back_state != tk.NORMAL:
    #             self.back_button.config(state=tk.NORMAL)
    #             self.back_state = tk.NORMAL
    #     else:
    #         if self.back_state != tk.DISABLED:
    #             self.back_button.config(state=tk.DISABLED)
    #             self.back_state = tk.DISABLED
    #     if browser.CanGoForward():
    #         if self.forward_state != tk.NORMAL:
    #             self.forward_button.config(state=tk.NORMAL)
    #             self.forward_state = tk.NORMAL
    #     else:
    #         if self.forward_state != tk.DISABLED:
    #             self.forward_button.config(state=tk.DISABLED)
    #             self.forward_state = tk.DISABLED
    #     self.after(100, self.update_state)

# side buttons? idk maybe


class SideButtons(tk.Frame):

    def __init__(self, root):
        tk.Frame.__init__(self, root)

        for row in range(2):
           for col in range(10):
                butt1 = tk.Button(self, bg='blue', width=1)
                butt1.grid(row=row, column=col)

# need to make two panels
# one for showing node infomation
# one for creating a new node
# needs to hook into

# class ViewPanel(tk.Frame):
#     def __init__(self, master):

#             self.back_state = tk.NONE
#             self.forward_state = tk.NONE
#             self.back_image = None
#             self.forward_image = None
#             self.reload_image = None

#             tk.Frame.__init__(self, master)
#             resources = os.path.join(os.path.dirname(__file__), "resources")


#             # Reload button
#             reload_png = os.path.join(resources, "reload"+IMAGE_EXT)
#             if os.path.exists(reload_png):
#                 self.reload_image = tk.PhotoImage(file=reload_png)
#             self.reload_button = tk.Button(self, image=self.reload_image,
#                                         command=self.reload)
#             self.reload_button.grid(row=0, column=2)


#     def reload(self):
#             if self.master.get_browser():
#                 self.master.get_browser().Reload()



#     def on_button1(self, _):
#             """For focus problems see Issue #255 and Issue #535. """
#             logger.debug("NavigationBar.on_button1")
#             self.master.master.focus_force()



if __name__ == '__main__':
    main()
