#
#   Name: Gavin Claire
#   Document: VisualizeGraph.py
#   Description: Allows for the graphing of the inputted devices 
#   and graph editing/inspecting functionality.
#

# Import Dependencies
import networkx as nx
from networkx.readwrite import json_graph

# Image URLs for graph nodes
defaultIcons = {
    "Desktop"  : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Desktop_V1.png",
    "Firewall" : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_FireWall_V1.png",
    "Laptop"   : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Laptop_V1.png",
    "Router"   : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Modem_V1.png",
    "Server"   : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Servers_V1.png",
    "Switch"   : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Switch_V1.png",
    "Printer"  : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Printer_V1.png",
    "IPPhone"  : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_IPPhone_V1.png"
}

shapeIcons = {
    "Desktop"  : "dot",
    "Firewall" : "square",
    "Laptop"   : "dot",
    "Router"   : "triangle",
    "Server"   : "star",
    "Switch"   : "diamond",
    "Printer"  : "dot",
    "IPPhone"  : "dot"
}

shapeColors = {
    "Desktop"  : "#6151E7",
    "Firewall" : "#E75151",
    "Laptop"   : "#b551E7",
    "Router"   : "#E9C46A",
    "Server"   : "#E76F51",
    "Switch"   : "#2A9D8F",
    "Printer"  : "#51E5E7",
    "IPPhone"  : "#51E76F"
}

# Containts the visulization struture for the graph
class GraphAttributes:
    #constructor
    def __init__(self, nodeSize = 20, icons = defaultIcons, fontColor = 'white', bgColor = '#222222', edgeWidth = 4, edgeColor = 'lightblue', graphStyle = "Shape"):
        self.nodeSize   = nodeSize
        self.icons      = icons
        self.fontColor  = fontColor
        self.bgColor    = bgColor
        self.edgeWidth  = edgeWidth
        self.edgeColor  = edgeColor
        self.graphStyle = graphStyle
        self.shape      = shapeIcons 

class VisualizeGraph:
    
    # Initialize the graph visulization
    def __init__(self, fileName = "nx.html", devices = None, graphAttributes = GraphAttributes()):
        self.fileName = fileName
        self.devices = devices
        self.gA = graphAttributes
        self.graphNX = nx.Graph()   # undirectional, no parallel edges
        if devices is not None:
            self.createGraph()
        else:
            self.updateGraph()

    # End the graph 
    def updateGraph(self):
        data1 = json_graph.node_link_data(self.graphNX)
        with open("sample.json", "w") as outfile:
            outfile.write(data1)

    # Create graph with class devices
    def createGraph(self):

        # Create the nodes within the graph
        for mac in self.devices:
            if self.gA.graphStyle == "Image":
                self.graphNX.add_node(mac, size = self.gA.nodeSize, text = mac, shape = 'image', image = self.gA.icons[self.devices[mac].deviceType])
            elif self.gA.graphStyle == "Shape":
                self.graphNX.add_node(mac, size = self.gA.nodeSize, text = mac, color = shapeColors[self.devices[mac].deviceType], shape = self.gA.shape[self.devices[mac].deviceType])
        
        # Create the edges within the graph
        for mac in self.devices:
            for neighborMAC in self.devices[mac].neighbors:
                self.graphNX.add_edge(mac, neighborMAC, color = self.gA.edgeColor, weight = self.gA.edgeWidth)

        self.updateGraph()

    # Add node to graph
    def addNode(self, node):

        nodeMACAddress = node.MACAddress

        # Add node to devices dictionary
        self.devices[nodeMACAddress] = node

        # Create the node within the graph
        if self.gA.graphStyle == "Image":
            self.graphNX.add_node(nodeMACAddress, size = self.gA.nodeSize, text = nodeMACAddress, shape = 'image', image = self.gA.icons[self.devices[nodeMACAddress].deviceType])
        elif self.gA.graphStyle == "Shape":
            self.graphNX.add_node(nodeMACAddress, size = self.gA.nodeSize, text = nodeMACAddress, color = shapeColors[self.devices[nodeMACAddress].deviceType], shape = self.gA.shape[self.devices[nodeMACAddress].deviceType])

        # Create the edges within the graph
        for neighborMAC in self.devices[nodeMACAddress].neighbors:
            self.graphNX.add_edge(nodeMACAddress, neighborMAC, color = self.gA.edgeColor, weight = self.gA.edgeWidth)
            
        self.updateGraph()

    # Add node to edge 
    def addEdge(self, startNodeMACAddress, endNodeMACAddress):

        # Add new neighbors to nodes
        self.devices[startNodeMACAddress].neighbors.append(endNodeMACAddress)
        self.devices[endNodeMACAddress].neighbors.append(startNodeMACAddress)

        # Create the edge within the graph
        self.graphNX.add_edge(startNodeMACAddress, endNodeMACAddress, color = self.gA.edgeColor, weight = self.gA.edgeWidth)
            
        self.updateGraph()

    # Remove node in graph
    def removeNode(self, nodeMACAddress):
        try:
            # Remove links from graph
            for neighborMAC in self.devices[nodeMACAddress].neighbors:
                self.removeEdge(nodeMACAddress, neighborMAC)
            
            # Remove node from graph
            self.graphNX.remove_node(nodeMACAddress)

            # Remove node from devices dictionary
            del self.devices[nodeMACAddress]

            self.updateGraph()
        except:
            None

    # Remove node in graph
    def removeEdge(self, startNodeMACAddress, endNodeMACAddress):

        # Remove neighbors from nodes
        if endNodeMACAddress in self.devices[startNodeMACAddress].neighbors:
            self.devices[startNodeMACAddress].neighbors.remove(endNodeMACAddress)
        if startNodeMACAddress in self.devices[endNodeMACAddress].neighbors:
            self.devices[endNodeMACAddress].neighbors.remove(startNodeMACAddress)

        # Remove edge from graph
        self.graphNX.remove_edge(startNodeMACAddress, endNodeMACAddress)

        self.updateGraph()


# HELPER FUNCTIONS

# Given an input list, return the flattened list
def flattenList(list):
    return [item for sublist in list for item in sublist]

# Convert graph data into text file to be exported to
def getGraphData():
    return "Graph Data"

import ProcessPackets as process
#  Hard coded data as an example of what the parsed data from a packet capture would look like. Loop through router first for each protocol
samplePackets = [
    {"SourceIP" : "192.168.0.2", "DestinationIP" : "192.168.0.3", "SourceMAC" : "00:10:7b:35:f5:b5", "DestinationMAC" : "00:10:7b:35:f5:c6", "Protocol" : "OSPF"},     # Packet from Router1 to Router2   ##
    {"SourceIP" : "192.168.0.6", "DestinationIP" : "192.168.0.7", "SourceMAC" : "00:10:7b:35:f5:b5", "DestinationMAC" : "00:10:7b:35:f5:d7", "Protocol" : "OSPF"},     # Packet from Router1 to Router3   ##
    {"SourceIP" : "192.168.10.10", "DestinationIP" : "192.168.10.11", "SourceMAC" : "00:10:7b:35:f5:c6", "DestinationMAC" : "00:10:7b:12:34:56", "Protocol" : "CDP"},  # Packet from Router2 to Switch0   ##
    {"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.12", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "94-ff-3c-1d-c9-05", "Protocol" : "NAT"},  # Packet from Switch0 to ASA0      ##
    {"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.13", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "fc:15:b4-1e-1d-77", "Protocol" : "SNMP"},  # Packet from Switch0 to Server3   ##
    {"SourceIP" : "192.168.10.20", "DestinationIP" : "192.168.10.21", "SourceMAC" : "00:10:7b:35:f5:c6", "DestinationMAC" : "00:10:7b:78:91:23", "Protocol" : "CDP"},  # Packet from Router2 to Switch1   ##
    {"SourceIP" : "192.168.10.21", "DestinationIP" : "192.168.10.22", "SourceMAC" : "00:10:7b:78:91:23", "DestinationMAC" : "F4-8E-38-EC-D7-10", "Protocol" : "WPA2"},  # Packet from Switch1 to Laptop3   ##
    {"SourceIP" : "192.168.10.21", "DestinationIP" : "192.168.10.23", "SourceMAC" : "00:10:7b:78:91:23", "DestinationMAC" : "F4-8E-38-EC-E8-10", "Protocol" : "WPA"},  # Packet from Switch1 to Laptop2   ##
    {"SourceIP" : "192.168.20.10", "DestinationIP" : "192.168.20.11", "SourceMAC" : "00:10:7b:35:f5:d7", "DestinationMAC" : "00:10:7b:45:67:89", "Protocol" : "CDP"},  # Packet from Router3 to Switch2   ##
    {"SourceIP" : "192.168.20.11", "DestinationIP" : "192.168.20.12", "SourceMAC" : "00:10:7b:45:67:89", "DestinationMAC" : "F4-8E-38-EC-F9-10", "Protocol" : "WPA2"},  # Packet from Switch2 to Laptop1   ##
    {"SourceIP" : "192.168.20.11", "DestinationIP" : "192.168.20.13", "SourceMAC" : "00:10:7b:45:67:89", "DestinationMAC" : "6C-E5-C9-98-76-54", "Protocol" : "DHCP"},  # Packet from Switch2 to PC2       ##
    {"SourceIP" : "192.168.20.20", "DestinationIP" : "192.168.20.21", "SourceMAC" : "00:10:7b:35:f5:d7", "DestinationMAC" : "00:10:7b:24:68:13", "Protocol" : "CDP"},  # Packet from Router3 to Switch3   ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.22", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "6C-E5-C9-78-90-23", "Protocol" : "HTTP"},  # Packet from Switch3 to PC1       ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.23", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "00-80-f0-a6-e4-99", "Protocol" : "VoIP"},  # Packet from Switch3 to IP Phone0 ##
    {"SourceIP" : "192.168.20.23", "DestinationIP" : "192.168.20.24", "SourceMAC" : "00-80-f0-a6-e4-99", "DestinationMAC" : "6C-E5-C9-12-34-56", "Protocol" : "DHCP"},  # Packet from IPPhone0 to PC0       ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.25", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "00-00-aa-37-32-36", "Protocol" : "IPP"},  # Packet from Switch3 to Printer1  ##
]

samplePackets2 = [
    {"SourceIP" : "192.168.0.2", "DestinationIP" : "192.168.0.3", "SourceMAC" : "00:10:7b:35:f5:b5", "DestinationMAC" : "00:10:7b:35:f5:c6", "Protocol" : "OSPF"},     # Packet from Router1 to Router2   ##
    {"SourceIP" : "192.168.0.6", "DestinationIP" : "192.168.0.7", "SourceMAC" : "00:10:7b:35:f5:b5", "DestinationMAC" : "00:10:7b:35:f5:d7", "Protocol" : "OSPF"},     # Packet from Router1 to Router3   ##
    {"SourceIP" : "192.168.10.10", "DestinationIP" : "192.168.10.11", "SourceMAC" : "00:10:7b:35:f5:c6", "DestinationMAC" : "00:10:7b:12:34:56", "Protocol" : "CDP"},  # Packet from Router2 to Switch0   ##
    {"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.12", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "94-ff-3c-1d-c9-05", "Protocol" : "NAT"},  # Packet from Switch0 to ASA0      ##
    {"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.13", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "8b-b1-44-1e-1d-77", "Protocol" : "SNMP"},  
]

# attributes = GraphAttributes(bgColor = '#000000', graphStyle = "Image")
# devices = process.getDevices(samplePackets)
# # graph = VisualizeGraph(devices = devices, fileName = "example.html", graphAttributes = attributes)

# print(repr(devices))







