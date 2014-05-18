#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^travelnote/(?P<pk>\d+)/$', views.TravelNoteDetailView.as_view(), name='travelnote_detail'),
    # TODO share list?
    # url(r'^list/$', views.HotelListView.as_view(), name='hotel_list'),
)
