import tkinter as tk
from pyvis.network import Network
import networkx as nx
import requests
import re
import sys
import json
import itertools

class Device:
    
    def __init__(self, packets = None, MAC = None):

        self.MACAddress = MAC
        self.IPAddress = set(self.getIP(packets))
        self.layer2Protocols = ["LLDP", "CDP", "IP route", "FDB", "ARP", "MLT", "CAN", "PPP"]
        self.layer3Protocols = ["CLNS", "DDP", "EGP", "EIGRP", "ICMP", "IGMP", "IPsec", "IPV4", "IPV6", "IPX", "OSPF", "PIM", "RIP", "IPv4", "IPv6", "HSRP"]
        self.deviceType = self.findDeviceType(packets)
        self.neighbors = self.getNeighbors(packets)
        self.vendor = self.getVendor()
        
    #def __init__(self, MAC, IPAddress, deviceType, neighbors, vendor):
      #  self.MACAddress = MAC
      #  self.IPAddress = IPAddress
      #  self.layer2Protocols = ["LLDP", "CDP", "IP route", "FDB", "ARP", "MLT", "CAN", "PPP"]
      #  self.layer3Protocols = ["CLNS", "DDP", "EGP", "EIGRP", "ICMP", "IGMP", "IPsec", "IPV4", "IPV6", "IPX", "OSPF", "PIM", "RIP", "IPv4", "IPv6", "HSRP"]
      #  self.deviceType = deviceType
      #  self.neighbors = neighbors
      #  self.vendor = vendor

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
        for packet in packets:
            if packet['Protocol'] in self.layer2Protocols and self.deviceType != "Layer3":
                self.deviceType = "Layer2"
            elif packet['Protocol'] in self.layer3Protocols:
                self.deviceType = "Layer3"
            elif packet['Protocol'] not in self.layer2Protocols or packet['Protocol'] not in self.layer3Protocols and not self.deviceType:
                self.deviceType = "EndDevice"
                    
            
        return self.deviceType
    
    def getVendor(self):
        return None
        try:
            response = requests.get(f"http://www.macvendorlookup.com/api/v2/%7Bself.MACAddress%7D/json", timeout=1)
            json_response = json.loads(response.text)
            return json_response[0]['company']
        except:
            response = requests.get(f"https://api.macvendors.com/%7Bself.MACAddress%7D", timeout=1)
            return response.text
            
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
    