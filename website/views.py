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
    else:
        with open("test.json") as json_file:
            nodeData = json.load(json_file)
            
        devices_dict = importDeviceData("test.json")
        nodes = getNodes(devices_dict)
        edges = getEdges(devices_dict)

        return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': json.dumps(nodeData)})

def edit(request):
    return render(request, 'edit.html')

def compare(request):
    return render(request, 'compare.html')

def export(request):
    return render(request, 'export.html')

def help(request):
    return render(request, 'help.html')