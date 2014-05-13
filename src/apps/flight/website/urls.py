#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', views.FlightDetailView.as_view(), name='flight_detail'),
    url(r'^list/$', views.FlightListView.as_view(), name='flight_list'),
)
