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
    path('inspect', views.inspect, name="inspect"),
    path('edit', views.edit, name="edit"),
    path('compare', views.compare, name="compare"),
    path('export', views.export, name="export"),
    path('help', views.help, name="help"),
]