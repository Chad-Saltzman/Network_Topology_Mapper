#
# Name: Gavin Claire
# Document: views.py
# Decription: Views for the website.
#


# turn off CSRF protection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


from django.shortcuts import render
import sys
import json
import logging as logger

def home(request):
    return render(request, 'home.html')

def inspect(request):

    nodes = [{'id': 1, 'label': 1, 'shape': 'dot', 'size': 2, 'title': 'n1'},
            {'id': 2, 'label': 2, 'shape': 'dot', 'size': 4, 'title': 'n2'},
            {'id': 3, 'label': 3, 'shape': 'dot', 'size': 6, 'title': 'n3'},
            {'id': 4, 'label': 3, 'shape': 'dot', 'size': 6, 'title': 'n3'}]
    edges = [
    ]
    
    return render(request, 'inspect.html', {'nodes': json.dumps(nodes), 'edges': json.dumps(edges)})

def edit(request):
    return render(request, 'edit.html')

def compare(request):
    return render(request, 'compare.html')

def export(request):
    return render(request, 'export.html')

def help(request):
    return render(request, 'help.html')


def TestCall(request):
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
    print >>sys.stderr, 'Goodbye, cruel world!'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def FormTestCall(request):
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
    last_name = request.POST.get('last_name', None)
    logger.critical(last_name)
    response = {
        'msg':'Your form has been submitted successfully' # response message
        }
    return JsonResponse(response)
    # if is_ajax(request=request):
    #     first_name = request.POST.get('first_name', None) # getting data from first_name input 
    #     last_name = request.POST.get('last_name', None)  # getting data from last_name input
    #     if first_name and last_name: #cheking if first_name and last_name have value
    #         response = {
    #                      'msg':'Your form has been submitted successfully' # response message
    #         }
    #         return JsonResponse(response) # return response as JSON
