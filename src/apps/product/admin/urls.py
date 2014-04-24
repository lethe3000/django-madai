#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^hotel/list$', views.HotelListView.as_view(), name='hotel_list'),
    url(r'^hotel/list.datatables$', views.HotelListDatatablesView.as_view(), name='hotel_list.datatables'),
    url(r'^hotel/create$', views.HotelCreateView.as_view(), name='hotel_create'),
    url(r'^hotel/(?P<pk>\d+)/edit$', views.HotelEditView.as_view(), name='hotel_edit'),
    url(r'^hotel/(?P<pk>\d+)/delete$', views.HotelDeleteView.as_view(), name='hotel_delete'),
    url(r'^hotel/(?P<pk>\d+)/preview$', views.HotelPreviewView.as_view(), name='hotel_preview'),
    url(r'^hotel/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.HotelUpdateView.as_view(), name='hotel_update'),
)

urlpatterns += patterns('',
   url(r'^flight/list$', views.FlightListView.as_view(), name='flight_list'),
   url(r'^flight/list.datatables$', views.FlightListDatatablesView.as_view(), name='flight_list.datatables'),
   url(r'^flight/create$', views.FlightCreateView.as_view(), name='flight_create'),
   url(r'^flight/(?P<pk>\d+)/edit$', views.FlightEditView.as_view(), name='flight_edit'),
   url(r'^flight/(?P<pk>\d+)/delete$', views.FlightDeleteView.as_view(), name='flight_delete'),
   url(r'^flight/(?P<pk>\d+)/preview$', views.FlightPreviewView.as_view(), name='flight_preview'),
   url(r'^flight/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.FlightUpdateView.as_view(), name='flight_update'),
)

# urlpatterns += patterns('',
#     url(r'^scenery/list$', views.SceneryListView.as_view(), name='scenery_list'),
#     url(r'^scenery/list.datatables$', views.SceneryListDatatablesView.as_view(), name='scenery_list.datatables'),
#     url(r'^scenery/create$', views.SceneryCreateView.as_view(), name='scenery_create'),
#     url(r'^scenery/(?P<pk>\d+)/edit$', views.SceneryEditView.as_view(), name='scenery_edit'),
#     url(r'^scenery/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.SceneryUpdateView.as_view(), name='scenery_update'),
#     url(r'^scenery/(?P<pk>\d+)/dashboard$', views.SceneryDashboardView.as_view(), name='scenery_dashboard'),
# )
#
# urlpatterns += patterns('',
#     url(r'^guidetype/list$', views.GuideTypeListView.as_view(), name='guidetype_list'),
#     url(r'^guidetype/list.datatables$', views.GuideTypeListDatatablesView.as_view(), name='guidetype_list.datatables'),
#     url(r'^guidetype/create$', views.GuideTypeCreateView.as_view(), name='guidetype_create'),
#     url(r'^guidetype/(?P<pk>\d+)/edit$', views.GuideTypeEditView.as_view(), name='guidetype_edit'),
#     url(r'^guidetype/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.GuideTypeUpdateView.as_view(), name='guidetype_update'),
# )
