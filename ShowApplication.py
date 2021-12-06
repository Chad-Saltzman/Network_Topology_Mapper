# -------------------------------------------------------------------
#
#   ShowApplication.py
#
#   Purpose: Display the application and GUI elements. Allow the
#   use to inspect/edit the network topology.
#
# -------------------------------------------------------------------

# Import Dependencies
from enum import auto
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network

from PIL import Image
import base64
import codecs

# Import DeviceProperties, VisualizeGraph, ProcessPackets
from DeviceProperties import Device, deviceTypes 
from VisualizeGraph import VisualizeGraph, GraphAttributes
import ProcessPackets as process

# Get Application Icons
icon = Image.open("Icons/NetDiscover_Logo.ico")
logo = Image.open("Icons/NetDiscover_Image.png")

# Configuration of Page
st.set_page_config(
    page_title = "NetDiscover",
    page_icon = icon,
    layout = "wide",
    initial_sidebar_state = "expanded",
)

# region Sample Packet Input/Graph

#  Hard coded data as an example of what the parsed data from a packet capture would look like. Loop through router first for each protocol
samplePackets = [
    {"SourceIP" : "192.168.0.2", "DestinationIP" : "192.168.0.3", "SourceMAC" : "00:10:7b:35:f5:b5", "DestinationMAC" : "00:10:7b:35:f5:c6", "Protocol" : "OSPF"},     # Packet from Router1 to Router2   ##
    {"SourceIP" : "192.168.0.6", "DestinationIP" : "192.168.0.7", "SourceMAC" : "00:10:7b:35:f5:b5", "DestinationMAC" : "00:10:7b:35:f5:d7", "Protocol" : "OSPF"},     # Packet from Router1 to Router3   ##
    {"SourceIP" : "192.168.10.10", "DestinationIP" : "192.168.10.11", "SourceMAC" : "00:10:7b:35:f5:c6", "DestinationMAC" : "00:10:7b:12:34:56", "Protocol" : "CDP"},  # Packet from Router2 to Switch0   ##
    {"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.12", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "3a-ac-1b-1d-c9-05", "Protocol" : "NAT"},  # Packet from Switch0 to ASA0      ##
    {"SourceIP" : "192.168.10.11", "DestinationIP" : "192.168.10.13", "SourceMAC" : "00:10:7b:12:34:56", "DestinationMAC" : "8b-b1-44-1e-1d-77", "Protocol" : "SNMP"},  # Packet from Switch0 to Server3   ##
    {"SourceIP" : "192.168.10.20", "DestinationIP" : "192.168.10.21", "SourceMAC" : "00:10:7b:35:f5:c6", "DestinationMAC" : "00:10:7b:78:91:23", "Protocol" : "CDP"},  # Packet from Router2 to Switch1   ##
    {"SourceIP" : "192.168.10.21", "DestinationIP" : "192.168.10.22", "SourceMAC" : "00:10:7b:78:91:23", "DestinationMAC" : "93-b7-be-34-ac-5f", "Protocol" : "WPA2"},  # Packet from Switch1 to Laptop3   ##
    {"SourceIP" : "192.168.10.21", "DestinationIP" : "192.168.10.23", "SourceMAC" : "00:10:7b:78:91:23", "DestinationMAC" : "91-f1-b5-5c-1a-cf", "Protocol" : "WPA"},  # Packet from Switch1 to Laptop2   ##
    {"SourceIP" : "192.168.20.10", "DestinationIP" : "192.168.20.11", "SourceMAC" : "00:10:7b:35:f5:d7", "DestinationMAC" : "00:10:7b:45:67:89", "Protocol" : "CDP"},  # Packet from Router3 to Switch2   ##
    {"SourceIP" : "192.168.20.11", "DestinationIP" : "192.168.20.12", "SourceMAC" : "00:10:7b:45:67:89", "DestinationMAC" : "7e-68-0b-b8-3d-29", "Protocol" : "WPA2"},  # Packet from Switch2 to Laptop1   ##
    {"SourceIP" : "192.168.20.11", "DestinationIP" : "192.168.20.13", "SourceMAC" : "00:10:7b:45:67:89", "DestinationMAC" : "0d-bf-cd-f4-40-9d", "Protocol" : "DHCP"},  # Packet from Switch2 to PC2       ##
    {"SourceIP" : "192.168.20.20", "DestinationIP" : "192.168.20.21", "SourceMAC" : "00:10:7b:35:f5:d7", "DestinationMAC" : "00:10:7b:24:68:13", "Protocol" : "CDP"},  # Packet from Router3 to Switch3   ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.22", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "1b-95-5b-93-4a-34", "Protocol" : "HTTP"},  # Packet from Switch3 to PC1       ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.23", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "9e-a9-c9-a6-e4-99", "Protocol" : "VoIP"},  # Packet from Switch3 to IP Phone0 ##
    {"SourceIP" : "192.168.20.23", "DestinationIP" : "192.168.20.24", "SourceMAC" : "9e-a9-c9-a6-e4-99", "DestinationMAC" : "89-61-86-23-44-38", "Protocol" : "DHCP"},  # Packet from IPPhone0 to PC0       ##
    {"SourceIP" : "192.168.20.21", "DestinationIP" : "192.168.20.25", "SourceMAC" : "00:10:7b:24:68:13", "DestinationMAC" : "f1-b0-44-37-32-36", "Protocol" : "IPP"},  # Packet from Switch3 to Printer1  ##
]



attributes = GraphAttributes(bgColor = '#000000')
devices = process.getDevices(samplePackets)
graph = VisualizeGraph(devices = devices, fileName = "example.html", graphAttributes = attributes)
graph2 = VisualizeGraph()
topologiesDict = {'Example Graph': graph, 'Empty Graph': graph2}



#endregion

# region METHODS

# Call this function whenever there is an update to the graph from one of the buttons - will reload the HTML file
def showHTMLTopology(fileName):
    # Read html file 
    try:
        HtmlFile = open(fileName, 'r', encoding='utf-8')

    except:
    # Can replace file with concrete 
        HtmlFile = open(fileName, 'r', encoding='utf-8')

    # Load HTML file in HTML components for display 
    # why is the height so small? 
    components.html(HtmlFile.read(), height = 800)

def getList(dict):
    list = []
    for key in dict.keys():
        list.append(key)
          
    return list

#endregion

#region MAIN PAGE

# Title and Caption
col1, mid, col2 = st.columns([1, 1, 45])
col1.image(logo, width = 60)
col2.title('NetDiscover')
st.caption('The Network Discovery and Inspection Application')

nodeMaps = getList(topologiesDict)
nodeMaps.append("Create New Topology")

# Select Network Topology or Open New
selectedMap = st.selectbox("Select Network Topology To Visualize", nodeMaps)

# Show file upload if 'Create New Topology' is selected
if selectedMap == 'Create New Topology':
    expander = st.expander(label = "Please Input Packet Capture", expanded = True)
    with expander:
        uploadedFile = st.file_uploader('')
        if expander.button('Create'):
            selectedMap = 'Topology1'
else:
    showHTMLTopology(topologiesDict[selectedMap].fileName)


    # Show device attributes

    attributes = ['MAC', 'IP Address', 'Device Type', 'Neighbors', 'Vendor']

    selectedAttributes = st.multiselect('Select device attribute(s) to view', attributes)

    # Show table of device attributes

    if len(selectedAttributes) > 0:
        cols = st.columns(len(selectedAttributes))
        nextCol = 0

        for attribute in attributes:
            if attribute in selectedAttributes:
                cols[nextCol].subheader(attribute)
                nextCol += 1

        nextCol = 0
        devices = topologiesDict[selectedMap].devices
        if (devices != None):
            for MAC in devices:
                device = devices[MAC]
                if 'MAC' in selectedAttributes:
                    cols[nextCol].write(MAC)
                    nextCol += 1
                if 'IP Address' in selectedAttributes:
                    cols[nextCol].write(device.getIPAddressesString())
                    nextCol += 1
                if 'Device Type' in selectedAttributes:
                    cols[nextCol].write(device.deviceType)
                    nextCol += 1
                if 'Neighbors' in selectedAttributes:
                    cols[nextCol].write(device.getNeighborsMACString())
                    nextCol += 1
                if 'Vendor' in selectedAttributes:
                    cols[nextCol].write(str(device.vendor))
                    nextCol += 1
                nextCol = 0

    #endregion

#region Sidebar Menu

# Sidebar title and menu options
st.sidebar.markdown("# Network Inspector")
currentMode = st.sidebar.radio(
    "Actions",
    ('View/Edit Node', 'Add Node', 'Remove Node', 'Analyze Networks')
)

# Change sidebar menu depending on CurrentMode
if currentMode == 'View/Edit Node':
    #need to import all nodes into this thing somehow, when a new node is selected in select box, update the rest of the boxes
    currentNodeSelect = st.sidebar.selectbox('Select a Node', topologiesDict[selectedMap].deviceMACs)

    # Get current device selected
    node = topologiesDict[selectedMap].devices[currentNodeSelect]

    # Show device attributes in order to be changed
    deviceTypeKeys = getList(deviceTypes)
    selectedNodeDeviceType = st.sidebar.selectbox('Device Type', deviceTypeKeys, index = deviceTypeKeys.index(node.deviceType))

    # Show Device IP Address so they can be changed
    
    i = 1
    for IP in node.IPAddress:
        st.sidebar.text_input("IP Address " + str(i), IP)
        i += 1

    vendor = st.sidebar.text_input('Vendor', node.vendor)

    EditNodeTime = st.sidebar.button('Update Device')
    if EditNodeTime:
        topologiesDict[selectedMap].devices[currentNodeSelect].MACAddress = "AAAAAAAAAA"

elif currentMode == 'Add Nodes':
    AddNodeSourceIP = st.sidebar.text_input('Source IP Address', '') 
    AddNodeDestinyIP = st.sidebar.text_input('Destination IP Address', '') 
    AddNodeSourceMAC = st.sidebar.text_input('Source MAC Address', '') 
    AddNodeDestinyMAC = st.sidebar.text_input('Destination MAC Address', '') 
    AddNodeDeviceType = st.sidebar.selectbox('Device Type',
                                        ['Desktop', 'Firewall', 'Laptop', 'Server', 'Switch', 'Printer', 'IPPhone'])
    NewNodeTime = st.sidebar.button('Add Node')

    if NewNodeTime:
        AddNodeFrontWrapper(AddNodeSourceIP, AddNodeDestinyIP, AddNodeSourceMAC, AddNodeDestinyMAC, AddNodeDeviceType)    


elif currentMode == 'Remove Nodes':
    # this select box needs to import in all existing nodes somehow, and pass it into delete nodefrontwrapper
    NodeToDelete = st.sidebar.selectbox('Select a Node',
                                        ['By event name', 'By GPS'])
    
    DeleteNodeTime = st.sidebar.button('Delete Node')
    if DeleteNodeTime:
        DeleteNodeFrontWrapper(NodeToDelete) 

elif CurrentMode == 'Analyze Networks':        
    #this won't do anything right now 
    AnalyzeType = st.sidebar.selectbox('Select Analysis',
                                        ['blib blob blib', 'taylors version'])   
    RunAnalysisTime = st.sidebar.button('Run Analysis')






# each one of these variables are what i think are needed to add a node
def AddNodeFrontWrapper(AddNodeSourceIP, AddNodeDestinyIP, AddNodeSourceMAC, AddNodeDestinyMAC, AddNodeDeviceType):
    # needs to invoke addNode and add edge in VisualizeGraph... and then refresh the nx.html
    # what exactly is a node data structure?

    print("blob")
    reloadHTML()

def DeleteNodeFrontWrapper(NodeToDelete):
    # needs to invoke removenode and remove edge in VisualizeGraph... and then refresh the nx.html
    # what exactly is a node data structure?

    print("blob")
    reloadHTML()

def EditNodeFrontWrapper(CurrentNodeSelect, SelectedNodeSourceIP, SelectedNodeDestinyIP, SelectedNodeSourceMAC, SelectedNodeDestinyMAC, SelectedNodeProtocol, SelectedNodeDeviceType):
    # not sure what this is supposed to invoke in visualizegraph tbh - maybe create new graph with new data and write new html file?

    print("blob")
    reloadHTML()












