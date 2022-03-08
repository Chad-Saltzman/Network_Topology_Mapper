#
# Name: Gavin Claire, Ronald Du, Chad Saltzman
# Document: views.py
# Decription: Views for the website.
#
from django.shortcuts import render
from website.python.DeviceDiscovery import *
from website.python.Comparison import *
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from django.core import serializers
import json

import logging as logger

TESTING = False

def home(request):
    print("home")
    # devices_dict = request.session.get('devices_dict', '')
    return render(request, 'home.html')

def inspectUpload(request):
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
    return render(request, 'upload.html')
    
def inspect(request):

    try:
        devices_dict = importDeviceData(json_string = request.session.get('devices_dict', ''))
        print(type(devices_dict))

    except:
        devices_dict = None
        pass

    if not TESTING:
        if  devices_dict:

            nodes = getNodes(devices_dict)
            edges = getEdges(devices_dict)

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

    try:
        devices_dict = importDeviceData(json_string = request.session.get('devices_dict', ''))
        print(type(devices_dict))

    except:
        devices_dict = None
        pass

    if not TESTING:
        if  devices_dict:

            nodes = getNodes(devices_dict)
            edges = getEdges(devices_dict)

            return render(request, 'edit.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': str(devices_dict).replace("'", '"')})
        else:
            return render(request, 'upload.html')
    else:
        with open("test.json") as json_file:
            nodeData = json.load(json_file)

        devices_dict = importDeviceData("test.json")
        request.session['devices_dict'] = str(devices_dict)
        nodes = getNodes(devices_dict)
        edges = getEdges(devices_dict)
        
        return render(request, 'edit.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges), 'nodeData': nodeData.replace("'", '"')})

def compare(request):

    try:
        compare_dict1 = importDeviceData(json_string = request.session.get('compare_dict1', ''))
        compare_dict2 = importDeviceData(json_string = request.session.get('compare_dict2', ''))
        comparison_dict = compareTopologies(compare_dict1, compare_dict2)
        nodesWhite = getNodes(comparison_dict["compTopology"], "")
        nodesRed = getNodes(comparison_dict["missTopology"], "Red")
        nodesGreen = getNodes(comparison_dict["newTopology"], "Green")

        edgesWhite = getEdges(comparison_dict["compTopology"])
        edgesRed = getEdges(comparison_dict["missTopology"])
        edgesGreen = getEdges(comparison_dict["newTopology"])

        nodes = (nodesWhite + nodesRed + nodesGreen)
        edges = (edgesWhite + edgesRed + edgesGreen)

    except:
        compare_dict1 = None
        compare_dict2 = None
        pass

    if not TESTING:
        if  compare_dict1 and compare_dict2:

            return render(request, 'compare.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges)})
        else:
            return render(request, 'comparisonUpload.html')

def comparisonUploadNew(request):
    return render(request, 'comparisonUpload.html')

def comparisonUpload(request):

    if request.method == 'POST' and request.FILES['myfile']:
        compare_dict1 = importDeviceData(str(request.FILES['myfile']))
        nodeData = json.loads(exportDeviceData(compare_dict1, write_true = False))

    if request.method == 'POST' and request.FILES['myfile2']:
        compare_dict2 = importDeviceData(str(request.FILES['myfile2']))
        nodeData2 = json.loads(exportDeviceData(compare_dict2, write_true = False))

    comparison_dict = compareTopologies(compare_dict1, compare_dict2)

    nodesWhite = getNodes(comparison_dict["compTopology"], "") or []
    nodesRed = getNodes(comparison_dict["missTopology"], "Red") or []
    nodesGreen = getNodes(comparison_dict["newTopology"], "Green") or []

    edgesWhite = getEdges(comparison_dict["compTopology"]) or []
    edgesRed = getEdges(comparison_dict["missTopology"]) or []
    edgesGreen = getEdges(comparison_dict["newTopology"]) or []

    nodes = (nodesWhite + nodesRed + nodesGreen)
    edges = (edgesWhite + edgesRed + edgesGreen)
    request.session['compare_dict1'] = str(compare_dict1)
    request.session['compare_dict2'] = str(compare_dict2)

    return render(request, 'compare.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges)})

def export(request):

    try:
        devices_dict = importDeviceData(json_string = request.session.get('devices_dict', ''))

    except:
        devices_dict = None
        pass

    if not TESTING:
        if  devices_dict:

            nodes = getNodes(devices_dict)
            edges = getEdges(devices_dict)

            return render(request, 'export.html', {'nodeData': str(devices_dict).replace("'", '"')})
        else:
            return render(request, 'upload.html')
    else:
        with open("test.json") as json_file:
            nodeData = json.load(json_file)

        devices_dict = importDeviceData("test.json")
        request.session['devices_dict'] = str(devices_dict)
        nodes = getNodes(devices_dict)
        edges = getEdges(devices_dict)
        
        return render(request, 'export.html', {'nodeData': nodeData.replace("'", '"')})

def help(request):
    return render(request, 'help.html')

def passDictionary(request):
    devices_dict = request.POST.get('dic', None)
    #logger.critical(devices_dict)

    request.session['devices_dict'] = str(devices_dict)

    return HttpResponse("", content_type='text/plain')

def passNetworkInformation(request):
    auth_dict = json.loads(request.POST.get('dic', None))
    # logger.critical(auth_dict)
    
    seed_IP = request.POST.get('IP', None)
    # logger.critical(seed_IP)
    # test = {"0.0.0.0/0":{"username":"netdiscover","password":"password"}}
    request.session['devices_dict'] = str(deviceDiscovery(seed_IP, auth_dict))

    return HttpResponse("", content_type='text/plain')