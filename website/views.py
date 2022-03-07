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

TESTING = True

def home(request):
    global devices_dict
    if 'devices_dict' not in globals():
        global devices_dict 
        devices_dict = {}
    if 'devices_dict2' not in globals():
        global devices_dict2
        devices_dict2 = {}
    if 'devices_dict3' not in globals():
        global devices_dict3
        devices_dict3 = {}
    return render(request, 'home.html')

def uploaddouble(request):
    global devices_dict
    return render(request, 'uploaddouble.html')

def upload2(request):
    global devices_dict
    if request.method == 'POST' and request.FILES['myfile']:
        devices_dict = importDeviceData(str(request.FILES['myfile']))
        nodeData = json.loads(exportDeviceData(devices_dict, write_true = False))
        nodes = getNodes(devices_dict)
        edges = getEdges(devices_dict)

    return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': json.dumps(nodeData)})

def upload3(request):
    global devices_dict
    if request.method == 'POST' and request.FILES['myfile']:
        devices_dict = importDeviceData(str(request.FILES['myfile']))
        nodeData = json.loads(exportDeviceData(devices_dict, write_true = False))
        nodes = getNodes(devices_dict)
        edges = getEdges(devices_dict)
    if request.method == 'POST' and request.FILES['myfile2']:
        devices_dict2 = importDeviceData(str(request.FILES['myfile2']))

    return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': json.dumps(nodeData)})
    
def upload(request):
    global devices_dict
    return render(request, 'upload.html')
    
def inspect(request):
    global devices_dict
    if not TESTING:
        # with open('currentfiledirectory.txt') as f:
        #     currentFileDirectory = f.readlines()
        
        # fileDirectory = currentFileDirectory[0].lstrip('/')

        # if fileDirectory != "":
        #     with open(fileDirectory) as json_file:
        #         nodeData = json.load(json_file)

        if not devices_dict:
            nodeData = json.loads(exportDeviceData(devices_dict, write_true = False))
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
    if not TESTING:
        if True:
            return render(request, 'edit.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': json.dumps(nodeData)})
        else:
            return render(request, 'upload.html')
    else:
        with open("test.json") as json_file:
            nodeData = json.load(json_file)

        devices_dict = importDeviceData("test.json")
        nodes = getNodes(devices_dict)
        edges = getEdges(devices_dict)

        return render(request, 'edit.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': json.dumps(nodeData)})

def compare(request):
    return render(request, 'compare.html')

def export(request):
    return render(request, 'export.html')

def help(request):
    return render(request, 'help.html')
    