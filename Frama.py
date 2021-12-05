# Import dependencies
from enum import auto
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network

#import device properties
from DeviceProperties import Device

#import visualize graph
from VisualizeGraph import VisualizeGraph

import base64

import codecs
# need this for favicon
from PIL import Image
# Read dataset // Not relevant in our situation
# df_interact = pd.read_csv('data/processed_drug_interactions.csv')

# if installed with python3 from windows store, run this file with    python -m streamlit run ./Frama.py


# need to hook all the functions for the sidebar into the visualize graph one 

# set very basic website details - including page title and favicon
favicon = Image.open("NetDiscover_Logo.ico")
TitleLogo = Image.open("NetDiscover_Logo.png")


st.set_page_config(
    page_title="NetDiscover",
    page_icon=favicon,
    layout="wide",
)


# Set header title and adds net discover image
st.image(TitleLogo,use_column_width=auto, width=100)
st.title('NetDiscover')


# Define selection options
node_maps = ['Toplogy1']

# This should allow multiple toplogies to be selected - need file upload
selected_map = st.multiselect('Select topology to visualize', node_maps)

# Set info message on initial site load
if len(selected_map) == 0:
    st.text('Please choose at least 1 topology to get started')


st.markdown("""
 * Use the menu at left to view more infomation on certain nodes or to edit nodes
 * The network topology will appear below
""")

#create a side bar for viewing infomation about nodes
#needs to display the source IP, destination IP, source mac, destination mac, and protocol and device type


# major problem but maybe acceptable:  we CANNOT know which node is selected inside of the nx.html file!
# my workaround: add a selectbox that let's us pick a node to view more infomation on - clunkyish, and when a node is selected, pull that info
# real solution: find someway to edit nx.html itself to send infomation to streamlit 

st.sidebar.markdown("# NetDiscover Menu")
CurrentMode = st.sidebar.radio(
    "Choose a Mode",
    ('View and Edit Nodes', 'Add Nodes', 'Remove Nodes', 'Analyze Networks')

)


# call this function whenever there is an update to the graph from one of the buttons - will reload the HTML file
def reloadHTML():
    # read html file 
    try:
        HtmlFile = open('nx.html', 'r', encoding='utf-8')

    except:
    # can replace file with concrete 
        HtmlFile = open('nx.html', 'r', encoding='utf-8')

    # Load HTML file in HTML components for display 
    # why is the height so small? 
    components.html(HtmlFile.read(), height = 1000)


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


if CurrentMode == 'View and Edit Nodes':
    #need to import all nodes into this thing somehow, when a new node is selected in select box, update the rest of the boxes
    CurrentNodeSelect = st.sidebar.selectbox('Select a Node',
                                        ['By event name', 'By GPS'])
    SelectedNodeSourceIP = st.sidebar.text_input('Source IP Address', '1126259462.4') 
    SelectedNodeDestinyIP = st.sidebar.text_input('Destination IP Address', '1126259462.4') 
    SelectedNodeSourceMAC= st.sidebar.text_input('Source MAC Address', '1126259462.4') 
    SelectedNodeDestinyMAC = st.sidebar.text_input('Destination MAC Address', '1126259462.4') 
    SelectedNodeProtocol = st.sidebar.selectbox('Protocol',
                                        ['By event name', 'By GPS'])
    SelectedNodeDeviceType = st.sidebar.selectbox('Device Type',
                                        ['By event name', 'By GPS'])
    EditNodeTime = st.sidebar.button('Edit Node')
    if EditNodeTime:
        EditNodeFrontWrapper(CurrentNodeSelect, SelectedNodeSourceIP, SelectedNodeDestinyIP, SelectedNodeSourceMAC, SelectedNodeDestinyMAC, SelectedNodeProtocol, SelectedNodeDeviceType)  





elif CurrentMode == 'Add Nodes':
    AddNodeSourceIP = st.sidebar.text_input('Source IP Address', '') 
    AddNodeDestinyIP = st.sidebar.text_input('Destination IP Address', '') 
    AddNodeSourceMAC = st.sidebar.text_input('Source MAC Address', '') 
    AddNodeDestinyMAC = st.sidebar.text_input('Destination MAC Address', '') 
    AddNodeDeviceType = st.sidebar.selectbox('Device Type',
                                        ['Desktop', 'Firewall', 'Laptop', 'Server', 'Switch', 'Printer', 'IPPhone'])
    NewNodeTime = st.sidebar.button('Add Node')

    if NewNodeTime:
        AddNodeFrontWrapper(AddNodeSourceIP, AddNodeDestinyIP, AddNodeSourceMAC, AddNodeDestinyMAC, AddNodeDeviceType)    


elif CurrentMode == 'Remove Nodes':
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


reloadHTML()




