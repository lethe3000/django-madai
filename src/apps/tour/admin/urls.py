#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^article/list$', views.ArticleListView.as_view(), name='article_list'),
    url(r'^article/list.datatables$', views.ArticleListDatatablesView.as_view(), name='article_list.datatables'),
    url(r'^article/create$', views.ArticleCreateView.as_view(), name='article_create'),
    url(r'^article/(?P<pk>\d+)/edit$', views.ArticleEditView.as_view(), name='article_edit'),
    url(r'^article/(?P<pk>\d+)/delete$', views.ArticleDeleteView.as_view(), name='article_delete'),
    url(r'^article/(?P<pk>\d+)/preview$', views.ArticlePreviewView.as_view(), name='article_preview'),
    url(r'^article/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.ArticleUpdateView.as_view(), name='article_update'),
)

urlpatterns += patterns('',
    url(r'^scenery/list$', views.SceneryListView.as_view(), name='scenery_list'),
    url(r'^scenery/list.datatables$', views.SceneryListDatatablesView.as_view(), name='scenery_list.datatables'),
    url(r'^scenery/create$', views.SceneryCreateView.as_view(), name='scenery_create'),
    url(r'^scenery/(?P<pk>\d+)/edit$', views.SceneryEditView.as_view(), name='scenery_edit'),
    url(r'^scenery/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.SceneryUpdateView.as_view(), name='scenery_update'),
    url(r'^scenery/(?P<pk>\d+)/dashboard$', views.SceneryDashboardView.as_view(), name='scenery_dashboard'),
)

urlpatterns += patterns('',
    url(r'^guidetype/list$', views.GuideTypeListView.as_view(), name='guidetype_list'),
    url(r'^guidetype/list.datatables$', views.GuideTypeListDatatablesView.as_view(), name='guidetype_list.datatables'),
    url(r'^guidetype/create$', views.GuideTypeCreateView.as_view(), name='guidetype_create'),
    url(r'^guidetype/(?P<pk>\d+)/edit$', views.GuideTypeEditView.as_view(), name='guidetype_edit'),
    url(r'^guidetype/(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.GuideTypeUpdateView.as_view(), name='guidetype_update'),
)
