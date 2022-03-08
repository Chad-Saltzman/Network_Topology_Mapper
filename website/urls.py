#
# Name: Gavin Claire
# Document: urls.py
# Decription: URLS for the website.
#

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('upload', views.upload, name="upload"),
    path('comparisonUpload', views.comparisonUpload, name="comparisonUpload"),
    path('comparisonUploadNew', views.comparisonUploadNew, name="comparisonUploadNew"),
    path('inspectUpload', views.inspectUpload, name="inspectUpload"),
    path('inspect', views.inspect, name="inspect"),
    path('edit', views.edit, name="edit"),
    path('compare', views.compare, name="compare"),
    path('export', views.export, name="export"),
    path('help', views.help, name="help"),
    path('passDictionary', views.passDictionary, name ="passDictionary"),
    path('passNetworkInformation', views.passNetworkInformation, name ="passNetworkInformation"),
]