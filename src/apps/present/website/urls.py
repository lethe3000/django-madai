#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from apps.present.website import views

urlpatterns = patterns('',
    url(r'^list/', views.PresentListView.as_view(), name='present_list'),
)