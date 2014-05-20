from django.conf import settings
from django.conf.urls import patterns, include, url

import django.contrib.admin

django.contrib.admin.autodiscover()


urlpatterns = patterns('',
    url(r'^', include('apps.website.urls', namespace='website')),
    url(r'^admin/', include('apps.admin.urls', namespace='admin')),
    url(r'^django_admin/', include(django.contrib.admin.site.urls)),
)

urlpatterns += patterns('',
    url(r'^download/android', 'apps.foundation.views.download_android_view'),
    url(r'^captcha/', include('captcha.urls')),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', dict(document_root=settings.MEDIA_ROOT)),
    )
