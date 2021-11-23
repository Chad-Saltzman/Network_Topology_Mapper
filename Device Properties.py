import dearpygui.dearpygui as dpg
import tkinter
from PIL import ImageTk, Image 


class Devices:
    
    def __init__(self, MACAddress, IPAddress, packets):
        self.MACAddress = MACAddress
        self.IPAddress = IPAddress
        self.deviceType = None 
        self.packets = packets 
        self.layer2Protocols = ["LLDP", "CDP", "IP route", "FDB", "ARP", "MLT", "CAN", "PPP"]
        self.layer3Protocols = ["CLNS", "DDP", "EGP", "EIGRP", "ICMP", "IGMP", "IPsec", "IPV4", "IPV6", "IPX", "OSPF", "PIM", "RIP"]
    
    def findDeviceType(self):
        for packet in self.packets:
            if packet['protocol'] in self.layer2Protocols and self.deviceType != "Layer3":
                self.deviceType = "Layer2"
            elif packet['protocol'] in self.layer3Protocols and self.deviceType != "Layer2":
                self.deviceType = "Layer3"
            elif packet['protocol'] not in self.layer2Protocols or packet['protocol'] not in self.layer3Protocols:
                continue
            else:
                self.deviceType = "Unidentifiable"  # Both layer2 and layer3 protocols appear for the device
        return self.deviceType

    def createDevice(self, deviceType):
        pass


img = Image.open("Somefile.png")
resized_img = img.resize((128, 108))
resized_img.save("resized_image.png")

dpg.create_context()

width, height, channels, data = dpg.load_image("resized_image.png") 
with dpg.texture_registry():
    texture_id = dpg.add_static_texture(width, height, data) 
 
with dpg.window(label="Tutorial", width = 800, height = 800):
    dpg.add_image(texture_id)

dpg.create_viewport(title='NetDiscover', width=800, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
 
