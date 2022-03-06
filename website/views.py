#
# Name: Gavin Claire
# Document: views.py
# Decription: Views for the website.
#

from django.shortcuts import render
from website.python.DeviceDiscovery import *
import json

TESTING = True

def home(request):
    return render(request, 'home.html')

def upload(request):
    return render(request, 'upload.html')
    
def inspect(request):

    if not TESTING:
        
        nodes = getNodes(devices_dict)
        edges = getEdges(devices_dict)

        return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges)})

    devices_dict = importDeviceData("test.json")
    
    nodes = getNodes(devices_dict)
    edges = getEdges(devices_dict)
    node_data = json.dumps(nodes)
    edge_data = json.dumps(edges)
    with open("node.txt", 'w') as temp_file:   
        temp_file.write(f"node data: {node_data}")

    with open("edge.txt", 'w') as temp_file:   
        temp_file.write(f"edge data: {edge_data}")
    
    return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges)})

def edit(request):
    return render(request, 'edit.html')

def compare(request):
    return render(request, 'compare.html')

def export(request):
    return render(request, 'export.html')

def help(request):
    return render(request, 'help.html')