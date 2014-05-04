#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^order/list$', views.OrderListView.as_view(), name='order_list'),
    url(r'^order/list.datatables$', views.OrderListDatatablesView.as_view(), name='order_list.datatables'),
    url(r'^order/create$', views.OrderCreateView.as_view(), name='order_create'),
    url(r'^order/(?P<pk>\d+)/edit$', views.OrderEditView.as_view(), name='order_edit'),
    url(r'^order/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.OrderUpdateView.as_view(), name='order_update'),
    url(r'^order/(?P<pk>\d+)/delete$', views.OrderDeleteView.as_view(), name='order_delete'),
)