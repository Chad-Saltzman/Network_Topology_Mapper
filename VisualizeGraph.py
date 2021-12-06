# -------------------------------------------------------------------
#
#   VisualizeGraph.py
#
#   Purpose: Allows for the graphing of the inputted devices 
#   and graph editing/inspecting functionality.
#
# -------------------------------------------------------------------

# Import Dependencies
from pyvis.network import Network
import networkx as nx

# Import DeviceProperties
from DeviceProperties import Device

# Image URLs for graph nodes
defaultIcons = {
    "Desktop"  : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Desktop_V1.png",
    "Firewall" : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_FireWall_V1.png",
    "Laptop"   : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Laptop_V1.png",
    "Router"   : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Modem_V1.png",
    "Server"   : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Servers_V1.png",
    "Switch"   : "https://raw.githubusercontent.com/Chad-Saltzman/Network_Topology_Mapper/main/Icons/NetDiscover_Icon_Switch_V1.png",
    "Printer"  : "icons/NetDiscover_Icon_Modem_Colored.png",
    "IPPhone"  : "icons/NetDiscover_Icon_Modem_Colored.png"
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

    def __init__(self, nodeSize = 20, icons = defaultIcons, fontColor = 'white', bgColor = '#222222', edgeWidth = 4, edgeColor = 'lightblue', graphStyle = "Shape"):
        self.nodeSize  = nodeSize
        self.icons     = icons
        self.fontColor = fontColor
        self.bgColor   = bgColor
        self.edgeWidth = edgeWidth
        self.edgeColor = edgeColor
        self.graphStyle = graphStyle
        if self.graphStyle == "Shape":
            self.shape = shapeIcons 
        else:
            self.shape = "image"

class VisualizeGraph:
    
    # Initialize the graph visulization
    def __init__(self, fileName = "nx.html", devices = None, graphAttributes = GraphAttributes()):
        self.fileName = fileName
        self.devices = devices
        self.deviceMACs = []
        self.gA = graphAttributes
        self.graphNX = nx.Graph()   # undirectional, no parallel edges
        self.graphNT = None
        if devices is not None:
            self.createGraph()
        else:
            self.updateGraph()

    # End the graph 
    def updateGraph(self):
        self.graphNT = Network(height='750px', width='100%', bgcolor=self.gA.bgColor, font_color=self.gA.fontColor)
        #region Options
        self.graphNT.set_options("""
                var options = {
                "configure": {
                    "enabled": false,
                    "filter": true
                },
                "edges": {
                    "color": {
                        "inherit": true
                    },
                    "smooth": {
                        "enabled": false,
                        "type": "continuous"
                    }
                },
                "interaction": {
                    "hover": true,
                    "dragNodes": true,
                    "hideEdgesOnDrag": false,
                    "hideNodesOnDrag": false,
                    "navigationButtons": true
                },
                "physics": {
                    "enabled": true,
                    "stabilization": {
                        "enabled": true,
                        "fit": true,
                        "iterations": 1000,
                        "onlyDynamicEdges": false,
                        "updateInterval": 50
                    }
                }
                }
                """)
        #endregion
        self.graphNT.from_nx(self.graphNX)
        self.graphNT.save_graph(self.fileName)

    # Create graph with class devices
    def createGraph(self):

        # Create the nodes within the graph
        for mac in self.devices:
            self.deviceMACs.append(mac)
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
        self.deviceMACs.append(nodeMACAddress)

        # Create the node within the graph
        if self.gA.graphStyle == "Image":
            self.graphNX.add_node(nodeMACAddress, size = self.gA.nodeSize, text = nodeMACAddress, shape = 'image', image = self.gA.icons[self.devices[nodeMACAddress].deviceType])
        elif self.gA.graphStyle == "Shape":
            self.graphNX.add_node(nodeMACAddress, size = self.gA.nodeSize, text = nodeMACAddress, color = shapeColors[self.devices[nodeMACAddress].deviceType], shape = self.gA.shape[node.devices[nodeMACAddress].deviceType])

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
        
        # Remove links from graph
        for neighborMAC in self.devices[nodeMACAddress].neighbors:
            self.removeEdge(nodeMACAddress, neighborMAC)
        
        # Remove node from graph
        self.graphNX.remove_node(nodeMACAddress)

        # Remove node from devices dictionary
        del self.devices[nodeMACAddress]
        #self.deviceMACs.remove(nodeMACAddress)

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

# Convert graph data into text file to be exported to
def getGraphData():
    return "Graph Data"
