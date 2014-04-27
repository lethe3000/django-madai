#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^article/list$', views.ArticleListView.as_view(), name='flightarticle_list'),
    url(r'^article/list.datatables$', views.ArticleListDatatablesView.as_view(), name='flightarticle_list.datatables'),
    url(r'^article/create$', views.ArticleCreateView.as_view(), name='flightarticle_create'),
    url(r'^article/(?P<pk>\d+)/edit$', views.ArticleEditView.as_view(), name='flightarticle_edit'),
    url(r'^article/(?P<pk>\d+)/delete$', views.ArticleDeleteView.as_view(), name='flightarticle_delete'),
    url(r'^article/(?P<pk>\d+)/preview$', views.ArticlePreviewView.as_view(), name='flightarticle_preview'),
    url(r'^article/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.ArticleUpdateView.as_view(), name='flightarticle_update'),
)

urlpatterns += patterns('',
    url(r'^flight/list$', views.FlightListView.as_view(), name='flight_list'),
    url(r'^flight/list.datatables$', views.FlightListDatatablesView.as_view(), name='flight_list.datatables'),
    url(r'^flight/create$', views.FlightCreateView.as_view(), name='flight_create'),
    url(r'^flight/(?P<pk>\d+)/edit$', views.FlightEditView.as_view(), name='flight_edit'),
    url(r'^flight/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.FlightUpdateView.as_view(), name='flight_update'),
    url(r'^flight/(?P<pk>\d+)/dashboard$', views.FlightDashboardView.as_view(), name='flight_dashboard'),
)

urlpatterns += patterns('',
    url(r'^infotype/list$', views.InfoTypeListView.as_view(), name='infotype_list'),
    url(r'^infotype/list.datatables$', views.InfoTypeListDatatablesView.as_view(), name='infotype_list.datatables'),
    url(r'^infotype/create$', views.InfoTypeCreateView.as_view(), name='infotype_create'),
    url(r'^infotype/(?P<pk>\d+)/edit$', views.InfoTypeEditView.as_view(), name='infotype_edit'),
    url(r'^infotype/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.InfoTypeUpdateView.as_view(), name='infotype_update'),
)