#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^create/', views.OrderCreateView.as_view(), name='order_create')
)
