#!/usr/bin/env python
# vim:fileencoding=utf-8
import hashlib
import json
import logging
from django.conf import settings
import os

from django import forms

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class WebCameraForm(forms.Form):

    data = forms.CharField(label=u'全球眼数据(Json)',
                           widget=forms.Textarea(attrs={'rows': 40}),
                           help_text="""格式如下{
"webcameraList":
[
    {
     "cameraid": "1",
     "scenery_id": "12",
     "name": "报国寺大门",
     "cameraurl": "rtsp://182.140.244.13/JQ/04007"
    }
]
""")

    def __init__(self, *args, **kwargs):
        super(WebCameraForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs['class'] = "col-md-10"

    def clean(self):
        if self.errors:
            return
        cleaned_data = super(WebCameraForm, self).clean()
        data = cleaned_data['data']
        try:
            json.loads(data)
        except:
            raise forms.ValidationError(u'请输入正确的数据')
        return cleaned_data

    def save(self, commit=True):
        sha1 = hashlib.sha1( self.cleaned_data['data'].encode('utf-8')).hexdigest()
        data = self.convert_thirdpary_data(json.loads(self.cleaned_data['data'], encoding='utf-8'))

        with open(settings.THIRDPARTY_WEBCAMERA_FILE, 'w') as f:
            raw = {"etag": sha1, "objects": data}
            json.dump(raw, f, indent=2)
            logger.debug("save webcamera content to file %s \n >> %s " % (settings.THIRDPARTY_WEBCAMERA_FILE, raw))

    def convert_thirdpary_data(self, thirdparty_data):
        #{
        #"webcameraList":
        #[
        #{
        # "cameraid": "1",
        # "scenery_id": "12",
        # "name": "报国寺大门",
        # "cameraurl": "rtsp://182.140.244.13/JQ/04007"
        #},
        #{
        # "cameraid": "2",
        # "scenery_id": "12",
        # "name": "零公里",
        # "cameraurl": "rtsp://182.140.244.13/JQ/04014"
        #},
        #{
        # "cameraid": "3",
        # "scenery_id": "12",
        # "name": "金顶四面佛",
        # "cameraurl": "rtsp://182.140.244.13/JQ/04009"
        #},
        #{
        # "cameraid": "4",
        # "scenery_id": "12",
        # "name": "金顶金殿和银殿",
        # "cameraurl": "rtsp://182.140.244.13/JQ/04012"
        #},
        #{
        # "cameraid": "5",
        # "scenery_id": "14",
        # "name": "肖公嘴睡佛",
        # "cameraurl": "rtsp://182.140.244.13/JQ/04006"
        #}
        #]
        #}
        res = []
        _, rows = thirdparty_data.popitem()
        for row in rows:
            item = {}
            for name, value in row.items():
                if name in ('cameraid'):
                    item['id'] = int(value)
                elif name in 'scenery_id':
                    item['scenery_id'] = int(value)
                elif name in ('cameraurl'):
                    item['web_link'] = value
                else:
                    item[name] = value
            res.append(item)
        return res


class Guide360Form(forms.Form):

    data = forms.CharField(label=u'全景360(只读)',
                           widget=forms.Textarea(attrs={'rows': 40, 'readonly': True},),
    )

    def __init__(self, *args, **kwargs):
        super(Guide360Form, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs['class'] = "col-md-10"
