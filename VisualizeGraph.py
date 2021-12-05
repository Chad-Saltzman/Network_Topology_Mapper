# -------------------------------------------------------------------
#
#   VisualizeGraph.py
#
#   Purpose: Allows for the graphing of the inputted devices 
#   and graph editing/inspecting functionality.
#
# -------------------------------------------------------------------

from pyvis.network import Network
import networkx as nx
from DeviceProperties import Device
import time

# Image URLs for graph nodes
defaultIcons = {
    "Desktop"  : "icons/NetDiscover_Icon_Desktop.png",
    "Firewall" : "icons/NetDiscover_Icon_FireWall.png",
    "Laptop"   : "icons/NetDiscover_Icon_Laptop.png",
    "Router"   : "icons/NetDiscover_Icon_Router.png",
    "Server"   : "icons/NetDiscover_Icon_Servers.png",
    "Switch"   : "icons/NetDiscover_Icon_Switch.png",
    "Printer"  : "icons/NetDiscover_Icon_Modem.png",
    "IPPhone"  : "icons/NetDiscover_Icon_Modem.png",
}

# Containts the visulization struture for the graph
class GraphAttributes:

    def __init__(self, nodeSize = 20, icons = defaultIcons, fontColor = 'white', bgColor = '#222222', edgeWidth = 4, edgeColor = 'lightblue'):
        self.nodeSize = nodeSize
        self.icons = icons
        self.fontColor = fontColor
        self.bgColor = bgColor
        self.edgeWidth = edgeWidth
        self.edgeColor = edgeColor

class VisualizeGraph:
    
    # Initialize the graph visulization
    def __init__(self, devices = None, graphAttributes = GraphAttributes()):
        self.devices = devices
        self.gA = graphAttributes
        self.graphNX = nx.Graph()   # undirectional, no parallel edges
        self.graphNT = None
        self.createGraph()

    # End the graph 
    def updateGraph(self):
        self.graphNT = Network(height='100%', width='100%', bgcolor=self.gA.bgColor, font_color=self.gA.fontColor)
        self.graphNT.toggle_physics(True)
        self.graphNT.barnes_hut(gravity=0, central_gravity=0, spring_length=0, spring_strength=0, damping=0, overlap=1)
        self.graphNT.from_nx(self.graphNX)
        self.graphNT.show('nx.html')

    # Create graph with class devices
    def createGraph(self):

        # Create the nodes within the graph
        for mac in self.devices:
            self.graphNX.add_node(mac, size = self.gA.nodeSize, text = mac, shape = 'image', image = self.gA.icons[self.devices[mac].deviceType])
        
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
        self.graphNX.add_node(nodeMACAddress, size = self.gA.nodeSize, text = nodeMACAddress, shape = 'image', image = self.gA.icons[self.devices[nodeMACAddress].deviceType])

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
    def removeNode(self, node):
        
        nodeMACAddress = node.MACAddress

        # Remove links from graph
        for neighborMAC in self.devices[nodeMACAddress].neighbors:
            self.removeEdge(nodeMACAddress, neighborMAC)

        # Remove node from graph
        self.graphNX.remove_node(node.MACAddress)

        # Remove node from devices dictionary
        del self.devices[node.MACAddress]

        self.updateGraph()

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
