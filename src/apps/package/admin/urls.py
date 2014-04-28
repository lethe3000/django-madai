#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
   url(r'^package/list$', views.PackageListView.as_view(), name='package_list'),
   url(r'^package/list.datatables$', views.PackageListDatatablesView.as_view(), name='package_list.datatables'),
   url(r'^package/create$', views.PackageCreateView.as_view(), name='package_create'),
   url(r'^package/(?P<pk>\d+)/edit$', views.PackageEditView.as_view(), name='package_edit'),
   url(r'^package/(?P<pk>\d+)/delete$', views.PackageDeleteView.as_view(), name='package_delete'),
   url(r'^package/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.PackageUpdateView.as_view(), name='package_update')
)