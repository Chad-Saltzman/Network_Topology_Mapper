#
# Name: Gavin Claire, Ronald Du
# Document: views.py
# Decription: Views for the website.
#

from django.shortcuts import render
from website.python.DeviceDiscovery import *
from django.conf import settings
from django.core.files.storage import FileSystemStorage


from django.core import serializers

from django.core import serializers
import json

import logging as logger

TESTING = False

def home(request):
    print("home")
    # devices_dict = request.session.get('devices_dict', '')
    return render(request, 'home.html')

def upload2(request):
    print("upload2")
    if request.method == 'POST' and request.FILES['myfile']:
        devices_dict = importDeviceData(str(request.FILES['myfile']))
        request.session['devices_dict'] = str(devices_dict)
        nodeData = str(devices_dict)
        # print("asdasdasasdasdasddsAD")
        nodes = getNodes(devices_dict)
        edges = getEdges(devices_dict)
        return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': nodeData.replace("'", '"')})
    # try:
        
    # except Expection as e:
    #     print("short error\n\n\n")
    
def upload(request):
    print("upload")
    return render(request, 'upload.html')
    
def inspect(request):


    print("inspect\n\n\n\nInspectINSPECT\n\n\n")
    devices_dict = importDeviceData(json_string = request.session.get('devices_dict', ''))
    print(type(devices_dict))

    if not TESTING:
        if  devices_dict:
            #nodeData = json.loads(exportDeviceData(devices_dict, write_true = False))
            nodes = getNodes(devices_dict)
            edges = getEdges(devices_dict)
            print(str(devices_dict))
            print("this should print")
            return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': str(devices_dict).replace("'", '"')})
        else:
            return render(request, 'upload.html')
    else:
        with open("test.json") as json_file:
            nodeData = json.load(json_file)

        devices_dict = importDeviceData("test.json")
        request.session['devices_dict'] = str(devices_dict)
        nodes = getNodes(devices_dict)
        edges = getEdges(devices_dict)
        
        return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': nodeData.replace("'", '"')})

def edit(request):
    print("edit")
    return render(request, 'edit.html')

def compare(request):
    print("compare")
    return render(request, 'compare.html')

def export(request):
    print("export")
    return render(request, 'export.html')

def help(request):
    print("help")
    return render(request, 'help.html')
    