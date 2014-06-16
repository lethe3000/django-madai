#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', views.KnowledgeDetailView.as_view(), name='knowledge_detail'),
    url(r'^list/$', views.KnowledgeListView.as_view(), name='knowledge_list'),
)
