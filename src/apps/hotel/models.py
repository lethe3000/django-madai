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

    def latest_hotel_article(self, hotel_id, info_type_id):
        articles = self.published_objects().filter(hotel=hotel_id, info_type=info_type_id)
        if articles:
            return articles.latest('created')
        else:
            return ArticleManager.get_empty_query_set(self)

    def latest_flight_article(self, flight_id, info_type_id):
        articles = self.published_objects().filter(flight=flight_id, info_type=info_type_id)
        if articles:
            return articles.latest('created')
        else:
            return ArticleManager.get_empty_query_set(self)


class BaseArticle(BaseModel):
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

    # hotel = models.ForeignKey('Hotel',
    #                           verbose_name=u'酒店',
    #                           related_name='articles')

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
        abstract = True


class HotelArticle(BaseArticle):
    hotel = models.ForeignKey('Hotel',
                              verbose_name=u'酒店',
                              related_name='articles')

    info_type = models.ForeignKey('InfoType',
                                  verbose_name=u'资料类型',
                                  related_name='articles')

    class Meta:
        verbose_name = u"酒店资讯"
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
        verbose_name = u"资料类型"
        ordering = ('display_order',)
        get_latest_by = "updated"


class HotelManager(models.Manager):

    def infotypes_with_article(self, hotel_id):
        res = OrderedDict()
        # fill with all of info types
        for infotype in InfoType.active_objects.only('id', 'name'):
            res[infotype.id] = {"name": infotype.name, "articles": []}
        # related the article with given info type
        for article in HotelArticle.objects.filter(hotel=hotel_id).select_related("info_type").only("title", 'info_type__id'):
            res[article.info_type.id]['articles'].append({"id": article.id, "title": article.title})
        return res


class ContentToImage(models.Model):
    """
    中间关系model. 记录content和image的关系.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    image = models.ForeignKey(Image, verbose_name=u'关联图片')
    display_order = models.PositiveIntegerField(verbose_name=u'显示顺序',
                                                default=0)

    def __unicode__(self):
        return unicode(self.image)

    def image_url(self):
        return self.image.url()

    def image_width(self):
        return self.image.width

    def image_height(self):
        return self.image.height

    class Meta:
        ordering = ('display_order',)
        abstract = True


class HotelImage(ContentToImage):
    pass


class Hotel(TimeBaseModel):
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

    images = generic.GenericRelation(HotelImage,
                                     blank=True,
                                     null=True,
                                     verbose_name=u'酒店图片集',
                                     related_name='products',
                                     help_text=u'用户可以看到的酒店展示图集，比如应用抓图、产品照片等')

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

    objects = HotelManager()
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

    def updated_timestamp(self):
        return int(self.updated.strftime("%s")) if self.updated else 0

    class Meta:
        verbose_name = u"酒店"
        ordering = ('display_order',)
        get_latest_by = "updated"
