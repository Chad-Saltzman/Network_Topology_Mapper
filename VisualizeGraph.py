# -------------------------------------------------------------------
#
#   VisualizeGraph.py
#
#   Purpose: 
# -------------------------------------------------------------------

from pyvis.network import Network
import networkx as nx
from DeviceProperties import Device

class Node:
    def __init(self, connections):
        self.connections = connections

class VisualizeGraph:
    
    def __init__(self, devices):
        self.graph = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
        self.createGraph(devices)

    def startEditGraph(self):
        self.graph.toggle_physics(True)

    def endEditGraph(self):
        self.graph.toggle_physics(False)
        self.graph.show('nx.html')

    def createGraph(self, devices):

        self.startEditGraph()

        # Create the nodes within the graph
        for device in devices:
            self.graph.add_node(devices[device].id, devices[device].MACAddress, title = devices[device].MACAddress)

            # Create the edges within the graph
            for neighbor in devices[device].neighbors:
                self.graph.add_edge(devices[device].id, neighbor.id, value = "edge")

        self.endEditGraph()

    def addNode(self, node, connectedNodes):
        
        self.startEditGraph()

        # Create the node within the graph
        self.graph.add_node(node, node, title = node)

        # Create the edges within the graph
        for connectedNode in connectedNodes:
            self.graph.add_edge(node, connectedNode, value = "edge")
            
        self.endEditGraph()

    def addEdge(self, startNode, endNode):
        
        self.startEditGraph()

        # Create the edges within the graph
        self.graph.add_edge(startNode, endNode, value = "edge")
            
        self.endEditGraph()






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
for device in Devices:
    print(Devices[device])


vg = VisualizeGraph(Devices)

#vg.AddNode("7", ["a", "1"] )

#vg.AddEdge("7", "A")