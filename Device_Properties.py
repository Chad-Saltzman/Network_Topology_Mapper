import tkinter as tk
from pyvis.network import Network
import networkx as nx
import requests
import re
import sys
import json


class Device:
    
    def __init__(self, packets, MAC):
        self.MACAddress = MAC
        self.IPAddress = set(self.getIP(packets))
        self.layer2Protocols = ["LLDP", "CDP", "IP route", "FDB", "ARP", "MLT", "CAN", "PPP"]
        self.layer3Protocols = ["CLNS", "DDP", "EGP", "EIGRP", "ICMP", "IGMP", "IPsec", "IPV4", "IPV6", "IPX", "OSPF", "PIM", "RIP", "IPv4", "IPv6", "HSRP"]
        self.deviceType = self.findDeviceType(packets)
        self.neighbors = self.getNeighbors(packets)
        self.vendor = self.getVendor()
        
    
    def __str__(self):
        return f"{self.MACAddress=}\n{self.IPAddress=}\n{self.deviceType=}\n{self.neighbors=}\n{self.vendor=}\n"

    def getIP(self, packets):
        IP_Addresses = []
        for packet in packets:
            device_end = "Source" if self.MACAddress == packet['SourceMAC'] else "Destination"
            if device_end == "Source":
                IP_Addresses.append(packet['SourceIP'])
            else:
                IP_Addresses.append(packet['DestinationIP'])
        return IP_Addresses
    
    def getNeighbors(self, packets):
        neighbors = []
        for packet in packets:
            for key in packet:
                if (key == "DestinationIP" or key == "SourceIP") and packet[key] not in neighbors and packet[key] not in self.IPAddress:
                    neighbors.append(packet[key])
        return neighbors

    def findDeviceType(self, packets):
        self.deviceType = None
        for packet in packets:
            if packet['Protocol'] in self.layer2Protocols and self.deviceType != "Layer3":
                self.deviceType = "Layer2"
            elif packet['Protocol'] in self.layer3Protocols:
                self.deviceType = "Layer3"
            elif packet['Protocol'] not in self.layer2Protocols or packet['Protocol'] not in self.layer3Protocols and not self.deviceType:
                self.deviceType = "EndDevice"
                    
            
        return self.deviceType
    
    def getVendor(self):
        try:
            response = requests.get(f"http://www.macvendorlookup.com/api/v2/{self.MACAddress}/json", timeout=1)
        except:
            print("Failed to get vendor")
            return None
        json_response = json.loads(response.text)
        return json_response[0]['company']

class Layer2(Device):

    def __init__(self, MAC, packet, IP=""):
        super().__init__(MAC, packet, IP)
        self.image = "Switch_Icon.png"

    def createDevice(self):
        pass
        
    
class Layer3(Device):
    def __init__(self, MAC, packet, IP):
        super().__init__(MAC, packet, IP)
        self.image = "Router_Icon.png"

    def createDevice(self):
        pass

def findUniqueMACs(packets):
    MAC_List = {}
    for packet in packets:
        if packet["SourceMAC"] not in MAC_List:
            MAC_List[packet["SourceMAC"]] = {packets.index(packet)}
        else:
            MAC_List[packet["SourceMAC"]].add(packets.index(packet))
        if packet["DestinationMAC"] not in MAC_List:
            MAC_List[packet["DestinationMAC"]] = {packets.index(packet)}
        else:
            MAC_List[packet["DestinationMAC"]].add(packets.index(packet))
    return MAC_List
#  Hard coded data as an example of what the parsed data from a packet capture would look like.
sample_Packets = [
    {"SourceIP" : "192.168.0.2", "DestinationIP" : "192.168.0.3", "SourceMAC" : "00:10:7b:35:f5:b5", "DestinationMAC" : "00:10:7b:35:f5:c6", "Protocol" : "OSPF"},     # Packet from Router1 to Router2   ##
    {"SourceIP" : "192.168.0.6", "DestinationIP" : "192.168.0.7", "SourceMAC" : "00:10:7b:35:f5:b5", "DestinationMAC" : "00:10:7b:35:f5:d7", "Protocol" : "OSPF"},     # Packet from Router1 to Router3   ##
    {"SourceIP" : "192.168.10.10", "DestinationIP" : "192.168.10.11", "SourceMAC" : "00:10:7b:35:f5:c6", "DestinationMAC" : "00:10:7b:12:34:56", "Protocol" : "CDP"},  # Packet from Router2 to Switch0   ##
    {"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.12", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "3a-ac-1b-1d-c9-05", "Protocol" : "ARP"},  # Packet from Switch0 to ASA0      ##
    {"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.13", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "8b-b1-44-1e-1d-77", "Protocol" : "ARP"},  # Packet from Switch0 to Server3   ##
    {"SourceIP" : "192.168.10.20", "DestinationIP" : "192.168.10.21", "SourceMAC" : "00:10:7b:35:f5:c6", "DestinationMAC" : "00:10:7b:78:91:23", "Protocol" : "CDP"},  # Packet from Router2 to Switch1   ##
    {"SourceIP" : "192.168.10.21", "DestinationIP" : "192.168.10.22", "SourceMAC" : "00:10:7b:78:91:23", "DestinationMAC" : "93-b7-be-34-ac-5f", "Protocol" : "ARP"},  # Packet from Switch1 to Laptop3   ##
    {"SourceIP" : "192.168.10.21", "DestinationIP" : "192.168.10.23", "SourceMAC" : "00:10:7b:78:91:23", "DestinationMAC" : "91-f1-b5-5c-1a-cf", "Protocol" : "ARP"},  # Packet from Switch1 to Laptop2   ##
    {"SourceIP" : "192.168.20.10", "DestinationIP" : "192.168.20.11", "SourceMAC" : "00:10:7b:35:f5:d7", "DestinationMAC" : "00:10:7b:45:67:89", "Protocol" : "CDP"},  # Packet from Router3 to Switch2   ##
    {"SourceIP" : "192.168.20.11", "DestinationIP" : "192.168.20.12", "SourceMAC" : "00:10:7b:45:67:89", "DestinationMAC" : "7e-68-0b-b8-3d-29", "Protocol" : "ARP"},  # Packet from Switch2 to Laptop1   ##
    {"SourceIP" : "192.168.20.11", "DestinationIP" : "192.168.20.13", "SourceMAC" : "00:10:7b:45:67:89", "DestinationMAC" : "0d-bf-cd-f4-40-9d", "Protocol" : "ARP"},  # Packet from Switch2 to PC2       ##
    {"SourceIP" : "192.168.20.20", "DestinationIP" : "192.168.20.21", "SourceMAC" : "00:10:7b:35:f5:d7", "DestinationMAC" : "00:10:7b:24:68:13", "Protocol" : "CDP"},  # Packet from Router3 to Switch3   ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.22", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "1b-95-5b-93-4a-34", "Protocol" : "ARP"},  # Packet from Switch3 to PC1       ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.23", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "9e-a9-c9-a6-e4-99", "Protocol" : "ARP"},  # Packet from Switch3 to IP Phone0 ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.24", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "89-61-86-23-44-38", "Protocol" : "ARP"},  # Packet from Switch3 to PC0       ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.25", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "f1-b0-44-37-32-36", "Protocol" : "ARP"},  # Packet from Switch3 to Printer1  ##
]
Devices = {}
MACS = findUniqueMACs(sample_Packets)
for i in range(len(MACS)):
    device_packets = []
    for index in MACS[list(MACS)[i]]:
        device_packets.append(sample_Packets[index])
    Devices[list(MACS)[i]] = Device(device_packets, list(MACS)[i])
for device in Devices:
    print(Devices[device])





























# from cefpython3 import cefpython as cef
# import ctypes
# try:
#     import tkinter as tk
# except ImportError:
#     import Tkinter as tk
# import sys
# import os
# import platform
# import logging as _logging

# Fix for PyCharm hints warnings
# WindowUtils = cef.WindowUtils()

# Platforms
# WINDOWS = (platform.system() == "Windows")
# LINUX = (platform.system() == "Linux")
# MAC = (platform.system() == "Darwin")

# Globals
# logger = _logging.getLogger("tkinter_.py")

# Constants
# Tk 8.5 doesn't support png images
# IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"


# class MainFrame(tk.Frame):

#     def __init__(self, root):
#         self.browser_frame = None
#         self.navigation_bar = None

#         Root
#         root.geometry("900x640")
#         tk.Grid.rowconfigure(root, 0, weight=1)
#         tk.Grid.columnconfigure(root, 0, weight=1)

#         MainFrame
#         tk.Frame.__init__(self, root)
#         self.master.title("Tkinter example")
#         self.master.protocol("WM_DELETE_WINDOW", self.on_close)
#         self.master.bind("<Configure>", self.on_root_configure)
#         self.setup_icon()
#         self.bind("<Configure>", self.on_configure)
#         self.bind("<FocusIn>", self.on_focus_in)
#         self.bind("<FocusOut>", self.on_focus_out)

#         NavigationBar
#         self.navigation_bar = NavigationBar(self)
#         self.navigation_bar.grid(row=0, column=0,
#                                  sticky=(tk.N + tk.S + tk.E + tk.W))
#         tk.Grid.rowconfigure(self, 0, weight=0)
#         tk.Grid.columnconfigure(self, 0, weight=0)

#         BrowserFrame
#         self.browser_frame = BrowserFrame(self, self.navigation_bar)
#         self.browser_frame.grid(row=1, column=0,
#                                 sticky=(tk.N + tk.S + tk.E + tk.W))
#         tk.Grid.rowconfigure(self, 1, weight=1)
#         tk.Grid.columnconfigure(self, 0, weight=1)

#         Pack MainFrame
#         self.pack(fill=tk.BOTH, expand=tk.YES)

#     def on_root_configure(self, _):
#         logger.debug("MainFrame.on_root_configure")
#         if self.browser_frame:
#             self.browser_frame.on_root_configure()

#     def on_configure(self, event):
#         logger.debug("MainFrame.on_configure")
#         if self.browser_frame:
#             width = event.width
#             height = event.height
#             if self.navigation_bar:
#                 height = height - self.navigation_bar.winfo_height()
#             self.browser_frame.on_mainframe_configure(width, height)

#     def on_focus_in(self, _):
#         logger.debug("MainFrame.on_focus_in")

#     def on_focus_out(self, _):
#         logger.debug("MainFrame.on_focus_out")

#     def on_close(self):
#         if self.browser_frame:
#             self.browser_frame.on_root_close()
#         self.master.destroy()

#     def get_browser(self):
#         if self.browser_frame:
#             return self.browser_frame.browser
#         return None

#     def get_browser_frame(self):
#         if self.browser_frame:
#             return self.browser_frame
#         return None

#     def setup_icon(self):
#         resources = os.path.join(os.path.dirname(__file__), "resources")
#         icon_path = os.path.join(resources, "tkinter"+IMAGE_EXT)
#         if os.path.exists(icon_path):
#             self.icon = tk.PhotoImage(file=icon_path)
#             noinspection PyProtectedMember
#             self.master.call("wm", "iconphoto", self.master._w, self.icon)


# class BrowserFrame(tk.Frame):

#     def __init__(self, master, navigation_bar=None):
#         self.navigation_bar = navigation_bar
#         self.closing = False
#         self.browser = None
#         tk.Frame.__init__(self, master)
#         self.bind("<FocusIn>", self.on_focus_in)
#         self.bind("<FocusOut>", self.on_focus_out)
#         self.bind("<Configure>", self.on_configure)
#         self.focus_set()

#     def embed_browser(self):
#         window_info = cef.WindowInfo()
#         rect = [0, 0, self.winfo_width(), self.winfo_height()]
#         window_info.SetAsChild(self.get_window_handle(), rect)
#         self.browser = cef.CreateBrowserSync(window_info,
#                                              url="file:///H:/Documents/GitHub/Network_Topology_Mapper/nx.html") #todo
#         assert self.browser
#         self.browser.SetClientHandler(LoadHandler(self))
#         self.browser.SetClientHandler(FocusHandler(self))
#         self.message_loop_work()

#     def get_window_handle(self):
#         if self.winfo_id() > 0:
#             return self.winfo_id()
#         elif MAC:
#             On Mac window id is an invalid negative value (Issue #308).
#             This is kind of a dirty hack to get window handle using
#             PyObjC package. If you change structure of windows then you
#             need to do modifications here as well.
#             noinspection PyUnresolvedReferences
#             from AppKit import NSApp
#             noinspection PyUnresolvedReferences
#             import objc
#             Sometimes there is more than one window, when application
#             didn't close cleanly last time Python displays an NSAlert
#             window asking whether to Reopen that window.
#             noinspection PyUnresolvedReferences
#             return objc.pyobjc_id(NSApp.windows()[-1].contentView())
#         else:
#             raise Exception("Couldn't obtain window handle")

#     def message_loop_work(self):
#         cef.MessageLoopWork()
#         self.after(10, self.message_loop_work)

#     def on_configure(self, _):
#         if not self.browser:
#             self.embed_browser()

#     def on_root_configure(self):
#         Root <Configure> event will be called when top window is moved
#         if self.browser:
#             self.browser.NotifyMoveOrResizeStarted()

#     def on_mainframe_configure(self, width, height):
#         if self.browser:
#             if WINDOWS:
#                 ctypes.windll.user32.SetWindowPos(
#                     self.browser.GetWindowHandle(), 0,
#                     0, 0, width, height, 0x0002)
#             elif LINUX:
#                 self.browser.SetBounds(0, 0, width, height)
#             self.browser.NotifyMoveOrResizeStarted()

#     def on_focus_in(self, _):
#         logger.debug("BrowserFrame.on_focus_in")
#         if self.browser:
#             self.browser.SetFocus(True)

#     def on_focus_out(self, _):
#         logger.debug("BrowserFrame.on_focus_out")
#         if self.browser:
#             self.browser.SetFocus(False)

#     def on_root_close(self):
#         if self.browser:
#             self.browser.CloseBrowser(True)
#             self.clear_browser_references()
#         self.destroy()

#     def clear_browser_references(self):
#         Clear browser references that you keep anywhere in your
#         code. All references must be cleared for CEF to shutdown cleanly.
#         self.browser = None


# class LoadHandler(object):

#     def __init__(self, browser_frame):
#         self.browser_frame = browser_frame

#     def OnLoadStart(self, browser, **_):
#         if self.browser_frame.master.navigation_bar:
#             self.browser_frame.master.navigation_bar.set_url(browser.GetUrl())


# class FocusHandler(object):

#     def __init__(self, browser_frame):
#         self.browser_frame = browser_frame

#     def OnTakeFocus(self, next_component, **_):
#         logger.debug("FocusHandler.OnTakeFocus, next={next}"
#                      .format(next=next_component))

#     def OnSetFocus(self, source, **_):
#         logger.debug("FocusHandler.OnSetFocus, source={source}"
#                      .format(source=source))
#         return False

#     def OnGotFocus(self, **_):
#         """Fix CEF focus issues (#255). Call browser frame's focus_set
#            to get rid of type cursor in url entry widget."""
#         logger.debug("FocusHandler.OnGotFocus")
#         self.browser_frame.focus_set()


# class NavigationBar(tk.Frame):
#     def __init__(self, master):
#         self.back_state = tk.NONE
#         self.forward_state = tk.NONE
#         self.back_image = None
#         self.forward_image = None
#         self.reload_image = None

#         tk.Frame.__init__(self, master)
#         resources = os.path.join(os.path.dirname(__file__), "resources")

#         Back button
#         back_png = os.path.join(resources, "back"+IMAGE_EXT)
#         if os.path.exists(back_png):
#             self.back_image = tk.PhotoImage(file=back_png)
#         self.back_button = tk.Button(self, image=self.back_image,
#                                      command=self.go_back)
#         self.back_button.grid(row=0, column=0)

#         Forward button
#         forward_png = os.path.join(resources, "forward"+IMAGE_EXT)
#         if os.path.exists(forward_png):
#             self.forward_image = tk.PhotoImage(file=forward_png)
#         self.forward_button = tk.Button(self, image=self.forward_image,
#                                         command=self.go_forward)
#         self.forward_button.grid(row=0, column=1)

#         Reload button
#         reload_png = os.path.join(resources, "reload"+IMAGE_EXT)
#         if os.path.exists(reload_png):
#             self.reload_image = tk.PhotoImage(file=reload_png)
#         self.reload_button = tk.Button(self, image=self.reload_image,
#                                        command=self.reload)
#         self.reload_button.grid(row=0, column=2)

#         Url entry
#         self.url_entry = tk.Entry(self)
#         self.url_entry.bind("<FocusIn>", self.on_url_focus_in)
#         self.url_entry.bind("<FocusOut>", self.on_url_focus_out)
#         self.url_entry.bind("<Return>", self.on_load_url)
#         self.url_entry.bind("<Button-1>", self.on_button1)
#         self.url_entry.grid(row=0, column=3,
#                             sticky=(tk.N + tk.S + tk.E + tk.W))
#         tk.Grid.rowconfigure(self, 0, weight=100)
#         tk.Grid.columnconfigure(self, 3, weight=100)

#         Update state of buttons
#         self.update_state()

#     def go_back(self):
#         if self.master.get_browser():
#             self.master.get_browser().GoBack()

#     def go_forward(self):
#         if self.master.get_browser():
#             self.master.get_browser().GoForward()

#     def reload(self):
#         if self.master.get_browser():
#             self.master.get_browser().Reload()

#     def set_url(self, url):
#         self.url_entry.delete(0, tk.END)
#         self.url_entry.insert(0, url)

#     def on_url_focus_in(self, _):
#         logger.debug("NavigationBar.on_url_focus_in")

#     def on_url_focus_out(self, _):
#         logger.debug("NavigationBar.on_url_focus_out")

#     def on_load_url(self, _):
#         if self.master.get_browser():
#             self.master.get_browser().StopLoad()
#             self.master.get_browser().LoadUrl(self.url_entry.get())

#     def on_button1(self, _):
#         """Fix CEF focus issues (#255). See also FocusHandler.OnGotFocus."""
#         logger.debug("NavigationBar.on_button1")
#         self.master.master.focus_force()

#     def update_state(self):
#         browser = self.master.get_browser()
#         if not browser:
#             if self.back_state != tk.DISABLED:
#                 self.back_button.config(state=tk.DISABLED)
#                 self.back_state = tk.DISABLED
#             if self.forward_state != tk.DISABLED:
#                 self.forward_button.config(state=tk.DISABLED)
#                 self.forward_state = tk.DISABLED
#             self.after(100, self.update_state)
#             return
#         if browser.CanGoBack():
#             if self.back_state != tk.NORMAL:
#                 self.back_button.config(state=tk.NORMAL)
#                 self.back_state = tk.NORMAL
#         else:
#             if self.back_state != tk.DISABLED:
#                 self.back_button.config(state=tk.DISABLED)
#                 self.back_state = tk.DISABLED
#         if browser.CanGoForward():
#             if self.forward_state != tk.NORMAL:
#                 self.forward_button.config(state=tk.NORMAL)
#                 self.forward_state = tk.NORMAL
#         else:
#             if self.forward_state != tk.DISABLED:
#                 self.forward_button.config(state=tk.DISABLED)
#                 self.forward_state = tk.DISABLED
#         self.after(100, self.update_state)


# if __name__ == '__main__':
#     logger.setLevel(_logging.INFO)
#     stream_handler = _logging.StreamHandler()
#     formatter = _logging.Formatter("[%(filename)s] %(message)s")
#     stream_handler.setFormatter(formatter)
#     logger.addHandler(stream_handler)
#     logger.info("CEF Python {ver}".format(ver=cef.__version__))
#     logger.info("Python {ver} {arch}".format(
#             ver=platform.python_version(), arch=platform.architecture()[0]))
#     logger.info("Tk {ver}".format(ver=tk.Tcl().eval('info patchlevel')))
#     assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"
#     sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
#     root = tk.Tk()
#     app = MainFrame(root)
#     Tk must be initialized before CEF otherwise fatal error (Issue #306)
#     cef.Initialize()
    
#     app.mainloop()
#     cef.Shutdown()