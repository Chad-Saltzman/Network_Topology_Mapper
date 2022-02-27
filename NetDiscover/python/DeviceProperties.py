# -------------------------------------------------------------------
#
#   DeviceProperties.py
#
#   Purpose: Allows for the creation of Device objects.
#   
#
# -------------------------------------------------------------------

import requests
import json
import time

# region HELPER
def getList(dict):
    list = []
    for key in dict.keys():
        list.append(key)
          
    return list
#endregion

# Device Initialisms
deviceTypes = {
    "Switch"  : ["LLDP", "CDP", "IP route", "FDB", "ARP", "MLT", "CAN", "PPP"],
    "Router"  : ["CLNS", "DDP", "EGP", "EIGRP", "ICMP", "IGMP", "IPsec", "IPV4", "IPV6", "IPX", "OSPF", "PIM", "RIP", "IPv4", "IPv6", "HSRP"],
    "Desktop" : ["HTTP", "DHCP"],
    "Laptop"  : ["802.11", "WPA2", "WPA"],
    "IPPhone" : ["SIP", "VoIP"],
    "Laptop"  : ["HTTP", "DHCP"],
    "Printer" : ["IPP", "LPD"],
    "Server"  : ["SNMP"],
    "Firewall": ["NAT"]
}

deviceTypeKeys = getList(deviceTypes)

class Device:
    
    # function to export the devices and stuff
    def __repr__(self):
        


    def __init__(self, packets = None, MAC = None):

        self.MACAddress = MAC
        self.IPAddress = set(self.getIP(packets))
        self.switchProtocols  = ["LLDP", "CDP", "IP route", "FDB", "ARP", "MLT", "CAN", "PPP"]
        self.routerProtocols  = ["CLNS", "DDP", "EGP", "EIGRP", "ICMP", "IGMP", "IPsec", "IPV4", "IPV6", "IPX", "OSPF", "PIM", "RIP", "IPv4", "IPv6", "HSRP"]
        self.desktopProtocol  = ["HTTP", "DHCP"]
        self.laptopProtocol   = ["802.11", "WPA2", "WPA"]
        self.IPPhoneProtocol  = ["SIP", "VoIP"]
        self.printerProtocol  = ["IPP", "LPD"]
        self.serverProtocol   = ["SNMP"]
        self.firewallProtocol = ["NAT"]
        try:
            self.deviceType = self.findDeviceType(packets)
        except:
            self.deviceType = "None"
        try:
            self.neighbors = self.getNeighbors(packets)
        except:
            self.neighbors = []
        try:
            self.vendor = self.getVendor()
        except:
            self.vendor = None

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
                if (key == "DestinationMAC" or key == "SourceMAC") and packet[key] not in neighbors and packet[key] not in self.MACAddress:
                    neighbors.append(packet[key])
        return neighbors

    def findDeviceType(self, packets):
        self.deviceType = None

        protocols_by_device = [self.routerProtocols, self.switchProtocols, self.firewallProtocol, self.IPPhoneProtocol, self.laptopProtocol, self.desktopProtocol, self.printerProtocol, self.serverProtocol]
        for packet in packets:
            for device_type in protocols_by_device:
                for protocol in device_type:
                    if packet['Protocol'] in self.routerProtocols:
                        self.deviceType = "Router"
                        return self.deviceType
                    elif packet['Protocol'] in self.switchProtocols and self.deviceType != "Router":
                        self.deviceType = "Switch"
                        return self.deviceType
                    elif packet['Protocol'] in self.firewallProtocol:
                        self.deviceType = "Firewall"
                        return self.deviceType
                    elif packet['Protocol'] in self.IPPhoneProtocol:
                        self.deviceType = "IPPhone"
                        return self.deviceType
                    elif packet['Protocol'] in self.laptopProtocol:
                        self.deviceType = "Laptop"
                        return self.deviceType
                    elif packet['Protocol'] in self.desktopProtocol:
                        self.deviceType = "Desktop"
                        return self.deviceType
                    elif packet['Protocol'] in self.printerProtocol:
                        self.deviceType = "Printer"
                        return self.deviceType
                    elif packet['Protocol'] in self.serverProtocol:
                        self.deviceType = "Server"
                        return self.deviceType
        #print(self.MACAddress)
        #print(packets)  
        #print(self.deviceType)  
        #print("\n\n\n")
        return self.deviceType
    
    def getVendor(self):
        try:
            response = requests.get(f"http://www.macvendorlookup.com/api/v2/{self.MACAddress}/json", timeout=1)
            json_response = json.loads(response.text)
            vendor = json_response[0]['company']
            time.sleep(0.5)
            if type(vendor) == str:
                return vendor
            else:
                 return "None"
        except:
            response = requests.get(f"https://api.macvendors.com/{self.MACAddress}", timeout=1)
            vendor = response.text 
            time.sleep(0.5)
            if type(vendor) == str:
                return response.text
            else:
                 return "None"
            

    def getNeighborsMACString(self):
        s = ""
        for neighbor in self.neighbors:
            s += str(neighbor)
            s += ", "
        return s

    def getIPAddressesString(self):
        s = ""
        for IP in self.IPAddress:
            s += str(IP)
            s += ", "
        return s
        

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

