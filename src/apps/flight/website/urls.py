#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^scenery/(?P<scenery>\d+)/article/list/(?P<page>\d+)/$', views.ArticleListView.as_view(), name='article_list'),
    url(r'^scenery/list/$', views.SceneryListView.as_view(), name='scenery_list'),
    url(r'^scenery/(?P<pk>\d+)/$', views.SceneryView.as_view(), name='scenery'),
    url(r'^article/(?P<scenery>\d+)/(?P<guide_type>\d+)/latest/$', views.LatestArticleContentView.as_view(), name='latest_article'),
)
