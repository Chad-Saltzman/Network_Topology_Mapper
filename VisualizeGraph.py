# -------------------------------------------------------------------
#
#   VisualizeGraph.py
#
#   Purpose: 
# -------------------------------------------------------------------

from pyvis.network import Network
import networkx as nx

class Node:
    def __init(self, connections):
        self.connections = connections

class VisualizeGraph:
    
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.graph = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
        self.CreateGraph()

    def StartEditGraph(self):
        self.graph.toggle_physics(True)

    def EndEditGraph(self):
        self.graph.toggle_physics(False)
        self.graph.show('nx.html')

    def CreateGraph(self):

        self.StartEditGraph()

        # Create the nodes within the graph
        for node in self.nodes:
            self.graph.add_node(node, node, title = node)

        # Create the edges within the graph
        for edge in self.edges:
            self.graph.add_edge(edge[0], edge[1], value = "edge")

        self.EndEditGraph()

    def AddNode(self, node, connectedNodes):
        
        self.StartEditGraph()

        # Create the node within the graph
        self.graph.add_node(node, node, title = node)

        # Create the edges within the graph
        for connectedNode in connectedNodes:
            self.graph.add_edge(node, connectedNode, value = "edge")
            
        self.EndEditGraph()

    def AddEdge(self, startNode, endNode):
        
        self.StartEditGraph()

        # Create the edges within the graph
        self.graph.add_edge(startNode, endNode, value = "edge")
            
        self.EndEditGraph()





vg = VisualizeGraph({"A", "a", "1"}, [ ["A", "a"], ["A", "1"] ])


vg.AddNode("7", ["a", "1"] )

vg.AddEdge("7", "A")