#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import json
import logging
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
import os
import requests

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))

# define the map form tour scenery to 360 guide
# TODO: call http://ip:port/getScenicList to get the thirdparty scenery list and map to my own ones.
SCENERY_MAP = {"1": 12, "2": 13}
APIS = [{'uri': 'getScenicAudiolist', 'id_base_index': 0},
        {'uri': 'getScenicPanoramaList', 'id_base_index': 100000}, ]


class Command(BaseCommand):
    """
    take the snapshot of thirdparty server that get the audio and panorama list
    should schedule it at cron every day.
    """
    option_list = BaseCommand.option_list + (
        make_option('-s', '--server',
                    action='store',
                    dest='server',
                    default="",
                    help='guide360 server address'),
        make_option('-d', '--output_dir',
                    action='store',
                    dest='output_dir',
                    default=os.path.join(settings.MEDIA_ROOT, settings.MEDIA_THIRDPARTY_PREFIX),
                    help='dir which guide360 file'),
        make_option('-t', '--test',
                    action='store_true',
                    dest='test',
                    default=False,
                    help='load the test data'),
    )

    def handle(self, *args, **options):
        self.server = options['server']

        data = []
        for api in APIS:
            if options['test']:
                thirdparty_data = self.get_test_data(api['uri'])
            else:
                thirdparty_data = self.get_thirdparty_data(api['uri'])
            data.extend(self.convert_thirdparty_data(thirdparty_data, api['id_base_index']))
        json_text = json.dumps(data)
        sha1 = hashlib.sha1(json_text).hexdigest()
        file_name = settings.THIRDPARTY_GUIDE360_FILE
        with open(file_name, 'w') as fp:
            #
            #{
            #    "etag": "adfadfadf",
            #    "objects": [
            #        "id": 11111,
            #        "name": "test",
            #        "scenery_id": 1111,
            #        "web_link": "http://xxxxx.mp3"
            #    ]
            #}
            raw = {"etag": sha1, "objects": data}
            json.dump(raw, fp)
            logger.debug("export content to file %s \n >> %s " % (file_name, raw))

    def get_thirdparty_data(self, uri):
        url = 'http://%s/%s' % (self.server, uri)
        logger.debug("access " + url + " to get content")
        r = requests.get(url)
        if r.status_code == 200:
            logger.debug("thirdparty data for %s \n >>%s" % (url, r.text))
            # extract the row from server response.
            return r.text
        return ""


    def convert_thirdparty_data(self, thirdparty_data, id_base_index):
        # http://ip:port/getScenicAudiolist
        #{
        #＂scenicAudioList＂:
        #    [
        #       {
        #       ＂audioid＂: ＂1＂, ,
        #       ＂scenicid＂: ＂2＂,
        #       ＂name＂: ＂张飞庙＂ ,
        #       ＂audiourl＂: ＂http://ip:port/xxxx.mp3＂
        #       }
        #    ]
        #}
        #
        # http://ip:port/getScenicPanoramaList
        #{
        #＂scenicpanoramaList＂:
        #[
        #    {
        #    ＂panoramaid＂: ＂1＂,
        #    ＂scenicid＂: ＂3＂,
        #    ＂name＂: ＂张飞庙＂,
        #    ＂picurl＂: ＂http://ip:port/xxxx.jpg＂
        #    },
        #]
        #}
        res = []
        _, rows = thirdparty_data.popitem()
        for row in rows:
            item = {}
            for name, value in row.items():
                if name in ('audioid', 'panoramaid'):
                    item['id'] = int(value) + id_base_index
                elif name in 'scenicid':
                    item['scenery_id'] = SCENERY_MAP[value]
                elif name in ('audiourl', 'picurl'):
                    item['web_link'] = value
                else:
                    item[name] = value
            res.append(item)
        return res


    def get_test_data(self, uri):
        if uri == 'getScenicAudiolist':
            data = {
                "scenicAudioList":
                    [
                        {
                            "audioid": "1",
                            "scenicid": "2",
                            "name": "张飞庙语音1",
                            "audiourl": "http://ip:port/1.mp3"
                        },
                        {
                            "audioid": "2",
                            "scenicid": "1",
                            "name": "张飞庙语音2",
                            "audiourl": "http://ip:port/2.mp3"
                        }

                    ]
            }
        else:
            data = {
                "scenicpanoramaList":
                    [
                        {
                            "panoramaid": "1",
                            "scenicid": "2",
                            "name": "张飞庙地图1",
                            "picurl": "http://ip:port/panorama/1.mp3"
                        },
                        {
                            "panoramaid": "2",
                            "scenicid": "1",
                            "name": "张飞庙地图2",
                            "picurl": "http://ip:port/panorama/2.mp3"
                        }

                    ]
            }
        return data

