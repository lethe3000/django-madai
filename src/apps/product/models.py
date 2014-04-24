#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apps.common.models import BaseModel, ActiveDataManager, ProductBaseModel
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from apps.foundation.models import unique_image_name
from utils import random


def unique_html_name(instance, filename):
    return '%s/%s' % (settings.MEDIA_CONTENT_PREFIX, random.gen_uuid_filename('html'))


class HotelManager(models.Manager):
    def published_objects(self):
        return self.get_query_set().filter(is_active=True, is_published=True)

    def hot_articles(self):
        # return self.published_objects() \
        #     .filter(guide_type=GuideType.GUIDE_TYPE_HOT) \
        #     .order_by('display_order')
        return None

    def banner_articles(self):
        return self.published_objects().filter(is_pinned=True)

    def event_articles(self):
        # return self.published_objects().filter(guide_type=GuideType.GUIDE_TYPE_EVENT)
        return None

    def latest_article(self, scenery_id, guide_type_id):
        # return self.published_objects() \
        #     .filter(scenery=scenery_id, guide_type=guide_type_id) \
        #     .latest('created')
        return None


class Hotel(ProductBaseModel):
    # 展示信息
    title = models.CharField(max_length=128,
                             verbose_name=u'标题',
                             unique=True)

    title_image_file = models.ImageField(upload_to=unique_image_name,
                                         blank=True,
                                         null=True,
                                         verbose_name=u'标题图片')

    summary = models.CharField(max_length=128,
                               verbose_name=u'简介',
                               default="",
                               blank=True)

    content_file = models.FileField(upload_to=unique_html_name,
                                    verbose_name=u'html文件')

    is_published = models.BooleanField(default=False,
                                       verbose_name=u'是否已发布')

    desc = models.TextField(verbose_name='描述',
                            default="",
                            blank=True)

    web_link = models.URLField(max_length=255,
                               verbose_name=u'web链接',
                               default='',
                               blank=True)

    is_pinned = models.BooleanField(default=False,
                                    blank=True,
                                    verbose_name=u'Banner显示')

    source = models.CharField(max_length=64,
                              verbose_name=u'来源',
                              blank=True,
                              default="")

    display_order = models.IntegerField(verbose_name=u'显示顺序',
                                        default=0,
                                        blank=True)

    def published_at_timestamp(self):
        return int(timezone.localtime(self.published_at).strftime("%s")) if self.published_at else 0

    def title_image_url(self):
        return settings.STATIC_DEFAULT_TITLE_IMAGE_URL if not self.title_image_file else self.title_image_file.url

    def __unicode__(self):
        return self.title

    STATUS_OK = 0
    STATUS_DELETE = -1

    def status(self):
        return self.STATUS_OK if self.is_published and self.is_active else self.STATUS_DELETE

    def content_url(self):
        return self.content_file.url

    def content_html(self):
        try:
            with open(self.content_file.path) as f:
                html = f.read()
        except IOError:
            html = u'无内容'
        return html

    def content_short_url(self):
        """
        a short content_url
        """
        return reverse("article_html", kwargs={'pk': self.id})

    def __unicode__(self):
        return self.title

    objects = HotelManager()

    active_objects = ActiveDataManager()

    class Meta:
        verbose_name = u"酒店"
        ordering = ('-updated',)
        get_latest_by = "updated"


class Flight(Hotel):
    class Meta:
        verbose_name = u'航班'
        ordering = ('-updated',)
        get_latest_by = "updated"


class Combo(BaseModel):
    # 打包的hotel和flight
    # name, time, hotel, flight, price, ...
    amount = models.DecimalField(max_digits=16,
                                 decimal_places=2,
                                 verbose_name=u'总价',
                                 default=0.0)

