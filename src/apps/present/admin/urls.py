#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
   url(r'^present/list$', views.PresentListView.as_view(), name='present_list'),
   url(r'^present/list.datatables$', views.PresentListDatatablesView.as_view(), name='present_list.datatables'),
   url(r'^present/create$', views.PresentCreateView.as_view(), name='present_create'),
   url(r'^present/(?P<pk>\d+)/edit$', views.PresentEditView.as_view(), name='present_edit'),
   url(r'^present/(?P<pk>\d+)/delete$', views.PresentDeleteView.as_view(), name='present_delete'),
   url(r'^present/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.PresentUpdateView.as_view(), name='present_update')
)

urlpatterns += patterns('',
   url(r'^presentcategory/list$', views.PresentCategoryListView.as_view(), name='presentcategory_list'),
   url(r'^presentcategory/list.datatables$', views.PresentCategoryListDatatablesView.as_view(), name='presentcategory_list.datatables'),
   url(r'^presentcategory/create$', views.PresentCategoryCreateView.as_view(), name='presentcategory_create'),
   url(r'^presentcategory/(?P<pk>\d+)/edit$', views.PresentCategoryEditView.as_view(), name='presentcategory_edit'),
   url(r'^presentcategory/(?P<pk>\d+)/delete$', views.PresentCategoryDeleteView.as_view(), name='presentcategory_delete'),
   url(r'^presentcategory/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.PresentCategoryUpdateView.as_view(), name='presentcategory_update')
)