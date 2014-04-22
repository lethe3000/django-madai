from django.conf.urls import patterns, url
from apps.thirdparty.views import WebCameraView, Guide360View

urlpatterns = patterns('',
    url(r'^webcamera/$', WebCameraView.as_view(), name='webcamera'),
    url(r'^guide360/$', Guide360View.as_view(), name='guide360'),
)

