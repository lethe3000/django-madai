#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
   url(r'^knowledge/list$', views.KnowledgeListView.as_view(), name='knowledge_list'),
   url(r'^knowledge/list.datatables$', views.KnowledgeListDatatablesView.as_view(), name='knowledge_list.datatables'),
   url(r'^knowledge/create$', views.KnowledgeCreateView.as_view(), name='knowledge_create'),
   url(r'^knowledge/(?P<pk>\d+)/edit$', views.KnowledgeEditView.as_view(), name='knowledge_edit'),
   url(r'^knowledge/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.KnowledgeUpdateView.as_view(), name='knowledge_update'),
)