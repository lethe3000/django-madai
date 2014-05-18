#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
   url(r'^travlenote/list$', views.TravelNoteListView.as_view(), name='travelnote_list'),
   url(r'^travlenote/list.datatables$', views.TravelNoteListDatatablesView.as_view(), name='travelnote_list.datatables'),
   url(r'^travlenote/create$', views.TravelNoteCreateView.as_view(), name='travelnote_create'),
   url(r'^travlenote/(?P<pk>\d+)/edit$', views.TravelNoteEditView.as_view(), name='travelnote_edit'),
   url(r'^travlenote/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.TravelNoteUpdateView.as_view(), name='travelnote_update'),
)