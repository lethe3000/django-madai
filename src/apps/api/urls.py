#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings

from django.conf.urls import patterns, url, include
from apps.api.views import *


urlpatterns = patterns('',
    url(r'^customer/login/$', LoginView.as_view(), name='login'),
    url(r'^customer/register/$', RegisterView.as_view(), name='register'),
    url(r'^customer/reset_password/$', ResetPasswordView.as_view(), name='reset_password'),
    url(r'^customer/avatar/update/$', CustomerAvatarView.as_view(), name='avatar_update'),
    url(r'^customer/profile/$', CustomerProfileDetailView.as_view(), name='customer_profile_detail'),
    url(r'^customer/profile/update/$', CustomerProfileUpdateView.as_view(), name='customer_profile_update'),
)

urlpatterns += patterns('',
    url(r'^checkin/$', CheckinView.as_view(), name='checkin'),
)

urlpatterns += patterns('',
    url(r'^tour/scenery/$', SceneryListView.as_view(), name='scenery_list'),
    url(r'^tour/guidetype/$', GuideTypeListView.as_view(), name='guidetype_list'),
    url(r'^tour/article/$', ArticleListView.as_view(), name='article_list'),
)

urlpatterns += patterns('',
    url(r'^album/list/$', AlbumListView.as_view(), name='album_list'),
    url(r'^album/create/$', AlbumCreateView.as_view(), name='album_create'),
    url(r'^album/(?P<pk>\d+)/delete/$', AlbumDeleteView.as_view(), name='album_delete'),
    url(r'^album/images/$', AlbumImageListView.as_view(), name='album_image_list'),
    url(r'^album/(?P<album>\d+)/image/upload/$', AlbumImageUploadView.as_view(), name='album_image_upload'),
    url(r'^album/image/(?P<pk>\d+)/delete/$', AlbumImageDeleteView.as_view(), name='album_image_delete'),
    url(r'^album/image/bulk_delete/$', AlbumImageBulkDeleteView.as_view(), name='album_image_bulk_delete'),
)

urlpatterns += patterns('',
    url(r'^journal/list/$', JournalListView.as_view(), name='journal_list'),
    url(r'^journal/create/$', JournalCreateView.as_view(), name='journal_create'),
    url(r'^journal/(?P<pk>\d+)/delete/$', JournalDeleteView.as_view(), name='journal_delete'),
)

urlpatterns += patterns('',
    url(r'^thirdparty/webcamera/$', ThirdpartyWebCamera.as_view(), name='thirdparty_webcamera'),
)

urlpatterns += patterns('',
    url(r'^chatroom/list/$', ChatroomListView.as_view(), name='chatroom_list'),
    url(r'^chatroom/create/$', ChatroomCreateView.as_view(), name='chatroom_create'),
    url(r'^chatroom/(?P<pk>\d+)/join/', ChatroomJoinView.as_view(), name='chatroom_join'),
    url(r'^chatroom/(?P<pk>\d+)/leave/', ChatroomLeaveView.as_view(), name='chatroom_leave'),
    url(r'^chatroom/messages/$', ChatroomMessageListView.as_view(), name='chatroom_message_list'),
    url(r'^chatroom/(?P<pk>\d+)/message/create/$', ChatroomMessageCreateView.as_view(), name='chatroom_message_create'),
    url(r'^chatroom/(?P<pk>\d+)/block_users/$', ChatroomBlockUsersView.as_view(), name='chatroom_block_users'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^docs/', include('rest_framework_swagger.urls')),
    )
