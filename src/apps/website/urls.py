#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'apps.website.views.index', name='index'),
)

urlpatterns += patterns('',
    url(r'^customer/', include('apps.customer.website.urls', namespace='customer')),
)

urlpatterns += patterns('',
    url(r'^hotel/', include('apps.hotel.website.urls', namespace='hotel')),
)

urlpatterns += patterns('',
    url(r'^package/', include('apps.package.website.urls', namespace='package')),
)