#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
import logging
from django.core.urlresolvers import reverse
from django.utils import timezone
import os
from django.conf import settings
from django.db import models
from apps.common.caches import SimpleCacheManager
from apps.common.models import BaseModel, ActiveDataManager, TimeBaseModel
from apps.foundation.models import unique_image_name
from utils import random

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


def unique_html_name(instance, filename):
    return '%s/%s' % (settings.MEDIA_CONTENT_PREFIX, random.gen_uuid_filename('html'))


class ArticleManager(models.Manager):
    def published_objects(self):
        return self.get_query_set().filter(is_active=True, is_published=True)

    def hot_articles(self):
        return self.published_objects() \
                   .filter(info_type=InfoType.INFO_TYPE_HOT) \
                   .order_by('display_order')

    def banner_articles(self):
        return self.published_objects().filter(is_pinned=True)

    def event_articles(self):
        return self.published_objects().filter(info_type=InfoType.INFO_TYPE_EVENT)

    def latest_article(self, hotel_id, info_type_id):
        return self.published_objects()\
                   .filter(hotel=hotel_id, info_type=info_type_id)\
                   .latest('created')


class Article(BaseModel):
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

    hotel = models.ForeignKey('Hotel',
                              verbose_name=u'酒店',
                              related_name='articles')

    info_type = models.ForeignKey('InfoType',
                                  verbose_name='资料类型',
                                  related_name='articles')

    desc = models.TextField(verbose_name=u'描述',
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

    objects = ArticleManager()

    active_objects = ActiveDataManager()

    cache_objects = SimpleCacheManager()

    class Meta:
        verbose_name = u"资讯"
        ordering = ('-updated',)
        get_latest_by = "updated"


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
        verbose_name = u"酒店资料类型"
        ordering = ('display_order',)
        get_latest_by = "updated"


class HotelManager(models.Manager):

    def infotypes_with_article(self, hotel_id):
        res = OrderedDict()
        # fill with all of info types
        for infotype in InfoType.active_objects.only('id', 'name'):
            res[infotype.id] = {"name": infotype.name, "articles": []}
        # related the article with given info type
        for article in Article.objects.filter(hotel=hotel_id).select_related("info_type").only("title", 'info_type__id'):
            res[article.info_type.id]['articles'].append({"id": article.id, "title": article.title})
        return res


class Hotel(TimeBaseModel):
    name = models.CharField(max_length=64,
                            verbose_name=u'名称',
                            unique=True)

    image_file = models.ImageField(upload_to=unique_image_name,
                                   blank=True,
                                   default="",
                                   verbose_name=u'图片')

    summary = models.CharField(max_length=128,
                               verbose_name=u'简介',
                               default="",
                               blank=True)

    phone_sos = models.CharField(max_length=64,
                                 verbose_name=u'急救电话',
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

    objects = HotelManager()
    active_objects = ActiveDataManager()
    cache_objects = SimpleCacheManager()

    def __unicode__(self):
        return self.name

    def image_url(self):
        return settings.STATIC_DEFAULT_TITLE_IMAGE_URL if not self.image_file else self.image_file.url

    class Meta:
        verbose_name = u"酒店"
        ordering = ('display_order',)
        get_latest_by = "updated"
