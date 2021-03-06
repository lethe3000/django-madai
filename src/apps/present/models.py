#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.safestring import SafeString
from apps.hotel.models import unique_html_name
from utils import pretty_price
from apps.common.models import BaseModel, ActiveDataManager
from apps.foundation.models import unique_image_name


class Present(BaseModel):
    name = models.CharField(max_length=128,
                            verbose_name=u'礼品名',
                            unique=True)

    image_file = models.ImageField(upload_to=unique_image_name,
                                   blank=True,
                                   default="",
                                   verbose_name=u'图片')

    desc = models.TextField(verbose_name=u'描述',
                            default="",
                            blank=True)

    price = models.IntegerField(verbose_name=u'价值',
                                default=0)

    is_published = models.BooleanField(default=False,
                                       verbose_name=u'是否已发布')

    is_pinned = models.BooleanField(default=False,
                                    verbose_name=u'是否首页显示')

    display_order = models.IntegerField(verbose_name=u'显示顺序',
                                        default=0,
                                        blank=True)

    content_file = models.FileField(upload_to=unique_html_name,
                                    verbose_name=u'html文件')

    active_objects = ActiveDataManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"礼品"
        get_latest_by = "updated"
        ordering = ('-display_order',)

    STATUS_OK = 0
    STATUS_DELETE = -1

    def content_url(self):
        return self.content_file.url

    def content_html(self):
        try:
            with open(self.content_file.path) as f:
                html = f.read()
        except IOError:
            html = u'无内容'
        except ValueError:
            html = u'无内容'
        return html

    def status(self):
        return self.STATUS_OK if self.is_published and self.is_active else self.STATUS_DELETE

    def get_pretty_price(self):
        return pretty_price(self.price)

    def image_url(self):
        return settings.STATIC_DEFAULT_TITLE_IMAGE_URL if not self.image_file else self.image_file.url

    def images_html(self):
        html = ""
        for image in self.images.all().order_by('display_order'):
            html += '<img src="%s"></img>' % image.image_url()
        return SafeString(html)


class PresentCategory(BaseModel):
    name = models.CharField(max_length=128,
                            verbose_name=u'礼物名',
                            unique=True)

    presents = models.ManyToManyField(Present,
                                      verbose_name=u'包含的礼品',
                                      related_name='present')

    is_published = models.BooleanField(default=False,
                                       verbose_name=u'是否已发布')

    class Meta:
        verbose_name = u"礼品分类"
        get_latest_by = "updated"