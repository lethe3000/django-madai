#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'apps.website.views.index', name='index'),
    url(r'^package_searching$', 'apps.website.views.package_searching', name='package_searching'),
    url(r'^legal$', 'apps.website.views.legal', name='legal'),
    url(r'^privacy$', 'apps.website.views.privacy', name='privacy'),
    url(r'^aboutus$', 'apps.website.views.aboutus', name='aboutus')
)

urlpatterns += patterns('',
    url(r'^customer/', include('apps.customer.website.urls', namespace='customer')),
)

urlpatterns += patterns('',
    url(r'^tour/', include('apps.tour.website.urls', namespace='tour')),
)