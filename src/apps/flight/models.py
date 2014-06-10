#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
import logging
from django.core.urlresolvers import reverse
from django.utils import timezone
import os
from django.conf import settings
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.safestring import SafeString

from apps.common.caches import SimpleCacheManager
from apps.common.models import BaseModel, ActiveDataManager, TimeBaseModel
from apps.foundation.models import unique_image_name
from utils import random, pretty_price
from apps.foundation.models import Image
from apps.hotel.models import BaseArticle, ContentToImage, unique_html_name

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class InfoType(TimeBaseModel):

    INFO_TYPE_HOT = 2

    INFO_TYPE_EVENT = 3

    INFO_TYPE_MAP = 11

    name = models.CharField(max_length=64,
                            verbose_name=u'名称',
                            unique=True)

    image_file = models.ImageField(upload_to=unique_image_name,
                                   blank=True,
                                   default="",
                                   verbose_name=u'图片')

    display_order = models.IntegerField(verbose_name=u'显示顺序',
                                        default=0)

    is_active = models.BooleanField(default=True,
                                    verbose_name=u'激活状态')

    summary = models.CharField(max_length=128,
                               verbose_name=u'简介',
                               default="",
                               blank=True)

    objects = models.Manager()
    active_objects = ActiveDataManager()
    cache_objects = SimpleCacheManager()

    def __unicode__(self):
        return self.name

    def image_url(self):
        return settings.STATIC_DEFAULT_TITLE_IMAGE_URL if not self.image_file else self.image_file.url

    class Meta:
        verbose_name = u"资料类型"
        ordering = ('display_order',)
        get_latest_by = "updated"


class FlightManager(models.Manager):
    def infotypes_with_article(self, flight_id):
        res = OrderedDict()
        # fill with all of info types
        for infotype in InfoType.active_objects.only('id', 'name'):
            res[infotype.id] = {"name": infotype.name, "articles": []}
            # related the article with given info type
        for article in FlightArticle.objects.filter(flight=flight_id).select_related("info_type").only("title", 'info_type__id'):
            res[article.info_type.id]['articles'].append({"id": article.id, "title": article.title})
        return res

    def get_query_set(self):
        return super(FlightManager, self).get_query_set().filter(is_active=True).order_by('display_order')


class FlightImage(ContentToImage):
    pass


class FlightArticle(BaseArticle):
    flight = models.ForeignKey('Flight',
                               verbose_name=u'航班',
                               related_name='articles')

    info_type = models.ForeignKey('InfoType',
                                  verbose_name='资料类型',
                                  related_name='articles')

    class Meta:
        verbose_name = u"航班资讯"
        ordering = ('-updated',)
        get_latest_by = "updated"


class Flight(TimeBaseModel):
    name = models.CharField(max_length=64,
                            verbose_name=u'名称',
                            unique=True)

    address = models.CharField(max_length=64,
                               verbose_name=u'地址',
                               default="",
                               blank=True)

    price = models.IntegerField(verbose_name=u'价格',
                                default=0)

    image_file = models.ImageField(upload_to=unique_image_name,
                                   blank=True,
                                   default="",
                                   verbose_name=u'图片')

    summary = models.CharField(max_length=128,
                               verbose_name=u'简介',
                               default="",
                               blank=True)

    # TODO remove
    images = generic.GenericRelation(FlightImage,
                                     blank=True,
                                     null=True,
                                     verbose_name=u'航班图片集',
                                     related_name='products',
                                     help_text=u'用户可以看到的航班展示图集，比如应用抓图、产品照片等')

    content_file = models.FileField(upload_to=unique_html_name,
                                    verbose_name=u'html文件')

    advantages = models.TextField(max_length=512,
                                  verbose_name=u'优势',
                                  default="",
                                  blank=True)

    phone_contact = models.CharField(max_length=64,
                                     verbose_name=u'联系电话',
                                     default="",
                                     blank=True)

    display_order = models.IntegerField(verbose_name=u'显示顺序',
                                        default=0)

    is_active = models.BooleanField(default=True,
                                    verbose_name=u'激活状态')

    is_published = models.BooleanField(default=False,
                                       verbose_name=u'发布状态')

    objects = FlightManager()
    active_objects = ActiveDataManager()
    cache_objects = SimpleCacheManager()

    def __unicode__(self):
        return self.name

    def image_url(self):
        return settings.STATIC_DEFAULT_TITLE_IMAGE_URL if not self.image_file else self.image_file.url

    def images_html(self):
        html = ""
        for image in self.images.all().order_by('display_order'):
            html += '<img src="%s"></img>' % image.image_url()
        return SafeString(html)

    def get_advantages(self):
        seperator = '\r\n'
        return filter(lambda x: x, self.advantages.split(seperator))

    def get_pretty_price(self):
        return pretty_price(self.price)

    def content_url(self):
        try:
            return self.content_file.url
        except ValueError:
            return u"无内容"

    def content_html(self):
        try:
            with open(self.content_file.path) as f:
                html = f.read()
        except IOError:
            html = u'无内容'
        except ValueError:
            html = u'value error'
        return html

    class Meta:
        verbose_name = u"航班"
        ordering = ('display_order',)
        get_latest_by = "updated"
