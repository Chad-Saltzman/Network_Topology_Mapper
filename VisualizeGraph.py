# -------------------------------------------------------------------
#
#   VisualizeGraph.py
#
#   Purpose: 
# -------------------------------------------------------------------

#from IPython.core.display import Image
from pyvis.network import Network
import networkx as nx
from DeviceProperties import Device
import time
import json

# Image URLs for graph nodes
icons = {
    "Layer2": "icons/NetDiscover_Icon_Desktop.png",
    "Layer3": "icons/NetDiscover_Icon_FireWall.png"
}

class VisualizeGraph:
    
    def __init__(self, devices):
        self.devices = devices
        self.graphNX = nx.Graph()
        self.graphNT = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
        self.createGraph()

    def startEditGraph(self):
        self.graphNT.toggle_physics(False)

    def endEditGraph(self):
        self.graphNT = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
        self.graphNT.toggle_physics(False)
        self.graphNT.from_nx(self.graphNX)
        self.graphNT.show('nx.html')

    # Create graph with class devices
    def createGraph(self):

        self.startEditGraph()

        # Create the nodes within the graph
        for mac in self.devices:
            self.graphNX.add_node(mac, size = 20, text = mac, shape = 'image', image = icons[self.devices[mac].deviceType])
        
        # Create the edges within the graph
        for mac in self.devices:
            for neighborMAC in self.devices[mac].neighbors:
                self.graphNX.add_edge(mac, neighborMAC)

        self.endEditGraph()

    # Add node to graph
    def addNode(self, node):
        
        self.startEditGraph()

        nodeMACAddress = node.MACAddress

        # Add node to devices dictionary
        self.devices[nodeMACAddress] = node

        # Create the node within the graph
        self.graphNX.add_node(nodeMACAddress, text = nodeMACAddress, shape = 'image', image = icons[self.devices[mac].deviceType])

        # Create the edges within the graph
        for neighborMAC in self.devices[nodeMACAddress].neighbors:
            self.graphNX.add_edge(nodeMACAddress, neighborMAC)
            
        self.endEditGraph()

    # Add node to edge 
    def addEdge(self, startNodeMACAddress, endNodeMACAddress):
        
        self.startEditGraph()

        # Add new neighbors to nodes
        self.devices[startNodeMACAddress].neighbors.append(endNodeMACAddress)
        self.devices[endNodeMACAddress].neighbors.append(startNodeMACAddress)

        # Create the edge within the graph
        self.graphNX.add_edge(startNodeMACAddress, endNodeMACAddress)
            
        self.endEditGraph()

    # Remove node in graph
    def removeNode(self, node):
        
        self.startEditGraph()

        nodeMACAddress = node.MACAddress

        # Remove links from graph
        for neighborMAC in self.devices[nodeMACAddress].neighbors:
            self.removeEdge(nodeMACAddress, neighborMAC)

        # Remove node from graph
        self.graphNX.remove_node(node.MACAddress,)

        # Remove node from devices dictionary
        del self.devices[node.MACAddress]

        self.endEditGraph()

    # Remove node in graph
    def removeEdge(self, startNodeMACAddress, endNodeMACAddress):
        
        self.startEditGraph()

        # Remove neighbors from nodes
        if endNodeMACAddress in self.devices[startNodeMACAddress].neighbors:
            self.devices[startNodeMACAddress].neighbors.remove(endNodeMACAddress)
        if startNodeMACAddress in self.devices[endNodeMACAddress].neighbors:
            self.devices[endNodeMACAddress].neighbors.remove(startNodeMACAddress)

        # Remove edge from graph
        self.graphNX.remove_edge(startNodeMACAddress, endNodeMACAddress)

        self.endEditGraph()

# Given an input list, return the flattened list
def flattenList(list):
    return [item for sublist in list for item in sublist]



# Test data

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

#for device in Devices:
  #  print(Devices[device])

d = Device([{"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.12", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "3a-ac-1b-1d-c9-05", "Protocol" : "ARP"}], "A")
e = Device([{"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.12", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "3a-ac-1b-1d-c9-05", "Protocol" : "ARP"}], "1")
    


vg = VisualizeGraph(Devices)

vg.addNode(d)
vg.addNode(e)
vg.addEdge("A", "1")
time.sleep(1)
vg.removeNode(d)
#vg.removeEdge("A", "1")
#vg.removeNode(d)
#vg.removeNode(e)
#vg.removeNode(d)

#vg.addEdge("A", "1")
#vg.removeEdge("A", "1")


#vg.createGraph()
#vg.AddNode("7", ["a", "1"] )

#vg.AddEdge("7", "A")