#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from apps.chatroom.admin import views

urlpatterns = patterns('',
    url(r'^chatroom/list$', views.ChatroomListView.as_view(), name='chatroom_list'),
    url(r'^chatroom/list.datatables$', views.ChatroomListDatatablesView.as_view(), name='chatroom_list.datatables'),
    url(r'^chatroom/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.ChatroomUpdateView.as_view(), name='chatroom_update'),
    url(r'^chatroom/(?P<pk>\d+)$', views.ChatroomDetailView.as_view(), name='chatroom_detail'),
)