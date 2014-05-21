#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from apps.common.models import BaseModel, ActiveDataManager, TimeBaseModel
from apps.hotel.models import ArticleManager, unique_html_name
from apps.common.caches import SimpleCacheManager
from apps.foundation.models import unique_image_name


class TravelNoteManager(models.Manager):
    def published_objects(self):
        return self.get_query_set().filter(is_active=True, is_published=True)

    def banner_notes(self):
        return self.published_objects().filter(is_pinned=True).order_by('display_order')


class TravelNote(BaseModel):
    title = models.CharField(max_length=128,
                             verbose_name=u'标题',
                             unique=True)

    content_file = models.FileField(upload_to=unique_html_name,
                                    verbose_name=u'html文件')

    is_published = models.BooleanField(default=False,
                                       verbose_name=u'是否已发布')

    is_pinned = models.BooleanField(default=False,
                                    blank=True,
                                    verbose_name=u'Banner显示')

    display_order = models.IntegerField(verbose_name=u'显示顺序',
                                        default=0,
                                        blank=True)

    fake_user = models.CharField(max_length=32,
                                 verbose_name=u'fake作者')

    fake_head_image = models.ImageField(upload_to=unique_image_name,
                                        blank=True,
                                        default="",
                                        verbose_name=u'fake作者头像')

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

    def image_url(self):
        return settings.STATIC_DEFAULT_TITLE_IMAGE_URL if not self.fake_head_image else self.fake_head_image.url

    objects = TravelNoteManager()

    active_objects = ActiveDataManager()

    cache_objects = SimpleCacheManager()

    class Meta:
        verbose_name = u"游记"
        ordering = ('-updated',)
        get_latest_by = "updated"
