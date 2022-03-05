from django.shortcuts import render, HttpResponse
import json

# Create your views here.
def main(request):
    data = {
        'name': 'Django',
        'author': 'Deekshant',
        'number': 1.0,
        'is_true': True,
        'color': 'red',
        'list': [1, 2, 3, 4, 5],
        'dict': {
            'name': 'Deekshant',
            'value': 1.0,
            'is_true': True,
        }
    }
    return render(request, 'main/landing.html', {'data': json.dumps(data)})