#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^image/upload$', views.upload_image_view)
)

urlpatterns += patterns('',
    url(r'^clientapp/list$', views.ClientAppListView.as_view(), name='clientapp_list'),
    url(r'^clientapp/list.datatables$', views.ClientAppListDatatablesView.as_view(), name='clientapp_list.datatables'),
    url(r'^clientapp/create$', views.ClientAppCreateView.as_view(), name='clientapp_create'),
    url(r'^clientapp/(?P<pk>\d+)/edit$', views.ClientAppEditView.as_view(), name='clientapp_edit'),
    url(r'^clientapp/(?P<pk>\d+)/delete$', views.ClientAppDeleteView.as_view(), name='clientapp_delete'),
)
