from django.http import HttpResponse
from django.shortcuts import render
from json import dumps

def home(request):
    return render(request, 'home.html')

def inspect(request):
    return render(request, 'inspect.html')

def edit(request):
    return render(request, 'edit.html')

def compare(request):
    return render(request, 'compare.html')

def export(request):
    return render(request, 'export.html')

def help(request):
    return render(request, 'help.html')