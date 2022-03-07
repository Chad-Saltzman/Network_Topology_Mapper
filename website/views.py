#
# Name: Gavin Claire
# Document: views.py
# Decription: Views for the website.
#

from django.shortcuts import render
from website.python.DeviceDiscovery import *
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import json

TESTING = False

def home(request):
    return render(request, 'home.html')

def upload(request):
    
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name.replace(' ', ''), myfile)
        uploaded_file_url = fs.url(filename)
        with open('currentfiledirectory.txt', 'w') as f:
            f.write(str(uploaded_file_url))
            
    return render(request, 'upload.html')
    
def inspect(request):

    if not TESTING:
        with open('currentfiledirectory.txt') as f:
            currentFileDirectory = f.readlines()
        
        fileDirectory = currentFileDirectory[0].lstrip('/')

        if fileDirectory != "":
            with open(fileDirectory) as json_file:
                nodeData = json.load(json_file)

            devices_dict = importDeviceData(fileDirectory)       
            nodes = getNodes(devices_dict)
            edges = getEdges(devices_dict)

            return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': json.dumps(nodeData)})
        else:
            return render(request, 'upload.html')
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
    