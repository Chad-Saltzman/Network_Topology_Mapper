# Import dependencies 
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network

# Read dataset // Not relevant in our situation 
# df_interact = pd.read_csv('data/processed_drug_interactions.csv')

# Set header title
st.title('NetDiscover')

# Define selection options 
node_maps = ['Toplogy1', 'Topology2', 'Topology3']

# Implement multiselect dropdown menu for option selection
selected_map = st.multiselect('Select toplogy to visualize', node_maps)

# Set info message on initial site load
if len(selected_map) == 0:
    st.text('Please choose at least 1 topology to get started')



# read html file 
try:
    HtmlFile = open(f'nx.html', 'r', encoding='utf-8')

except:
    # can replace file with concrete 
    HtmlFile = open(f'nx.html', 'r', encoding='utf-8')

# Load HTML file in HTML components for display 
components.html(HtmlFile.read(), height=435)