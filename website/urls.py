#
# Name: Gavin Claire
# Document: urls.py
# Decription: URLS for the website.
#

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="start"),
    path('home', views.home, name="home"),
    path('upload', views.upload, name="upload"),
    path('upload2', views.upload2, name="upload2"),
    path('uploaddouble', views.uploaddouble, name="uploaddouble"),
    path('upload3', views.upload3, name="upload3"),
    path('inspect', views.inspect, name="inspect"),
    path('edit', views.edit, name="edit"),
    path('compare', views.compare, name="compare"),
    path('export', views.export, name="export"),
    path('help', views.help, name="help"),
]