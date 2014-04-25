#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^searching$', 'apps.package.website.views.searching', name='package_searching'),
)