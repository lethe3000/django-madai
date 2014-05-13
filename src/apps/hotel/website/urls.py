#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', views.HotelDetailView.as_view(), name='hotel_detail'),
    url(r'^list/$', views.HotelListView.as_view(), name='hotel_list'),
)
