#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^article/list$', views.ArticleListView.as_view(), name='hotelarticle_list'),
    url(r'^article/list.datatables$', views.ArticleListDatatablesView.as_view(), name='hotelarticle_list.datatables'),
    url(r'^article/create$', views.ArticleCreateView.as_view(), name='hotelarticle_create'),
    url(r'^article/(?P<pk>\d+)/edit$', views.ArticleEditView.as_view(), name='hotelarticle_edit'),
    url(r'^article/(?P<pk>\d+)/delete$', views.ArticleDeleteView.as_view(), name='hotelarticle_delete'),
    url(r'^article/(?P<pk>\d+)/preview$', views.ArticlePreviewView.as_view(), name='hotelarticle_preview'),
    url(r'^article/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.ArticleUpdateView.as_view(), name='hotelarticle_update'),
)

urlpatterns += patterns('',
    url(r'^hotel/list$', views.HotelListView.as_view(), name='hotel_list'),
    url(r'^hotel/list.datatables$', views.HotelListDatatablesView.as_view(), name='hotel_list.datatables'),
    url(r'^hotel/create$', views.HotelCreateView.as_view(), name='hotel_create'),
    url(r'^hotel/(?P<pk>\d+)/edit$', views.HotelEditView.as_view(), name='hotel_edit'),
    url(r'^hotel/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.HotelUpdateView.as_view(), name='hotel_update'),
    url(r'^hotel/(?P<pk>\d+)/dashboard$', views.HotelDashboardView.as_view(), name='hotel_dashboard'),
)

urlpatterns += patterns('',
    url(r'^infotype/list$', views.InfoTypeListView.as_view(), name='infotype_list'),
    url(r'^infotype/list.datatables$', views.InfoTypeListDatatablesView.as_view(), name='infotype_list.datatables'),
    url(r'^infotype/create$', views.InfoTypeCreateView.as_view(), name='infotype_create'),
    url(r'^infotype/(?P<pk>\d+)/edit$', views.InfoTypeEditView.as_view(), name='infotype_edit'),
    url(r'^infotype/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.InfoTypeUpdateView.as_view(), name='infotype_update'),
)
