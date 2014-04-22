#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.db.models import permalink
from django.conf import settings
import os
from sorl.thumbnail import ImageField
from apps.common.models import TimeBaseModel, ActiveDataManager
from apps.imagestore.utils import get_file_path

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class Album(TimeBaseModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'用户', null=True, blank=True, related_name='albums')

    name = models.CharField(u'名称', max_length=100, blank=False, null=False)

    is_public = models.BooleanField(u'是否公共开放', default=False)

    head = models.ForeignKey('AlbumImage', related_name='head_of', null=True, blank=True,
                             on_delete=models.SET_NULL)

    order = models.IntegerField(u'显示顺序', default=0)

    is_active = models.BooleanField(default=True,
                                    verbose_name=u'激活状态')

    objects = models.Manager()

    active_objects = ActiveDataManager()

    def get_head(self):
        if self.head:
            return self.head
        else:
            if self.images.all().count() > 0:
                self.head = self.images.all()[0]
                self.save()
                return self.head
            else:
                return None

    def updated_timestamp1(self):
        return int(self.updated.strftime("%s")) if self.updated else 0


    @permalink
    def get_absolute_url(self):
        return 'imagestore:album', (), {'album_id': self.id}

    def __unicode__(self):
        return self.name

    def deactivate(self):
        self.is_active = False
        for image in self.images.only('is_active', 'image').all():
            image.deactivate()
        self.save()

    class Meta:
        ordering = ('order', '-created', 'name')
        get_latest_by = "updated"


class AlbumImage(TimeBaseModel):

    title = models.CharField(u'标题', max_length=100, blank=True, default="")
    description = models.TextField(u'描述', blank=True, null=True, default="")
    order = models.IntegerField(u'显示顺序', default=0)
    image = ImageField(verbose_name=u'图片', upload_to=get_file_path)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'用户', null=True, blank=True, related_name='images')
    album = models.ForeignKey('Album', verbose_name=u'相册', null=True, blank=True, related_name='images')

    is_active = models.BooleanField(default=True,
                                    verbose_name=u'激活状态')

    objects = models.Manager()

    active_objects = ActiveDataManager()

    def deactivate(self):
        if self.image and os.path.exists(self.image.path):
            os.unlink(self.image.path)
        else:
            logger.warn("why not find the image? " + unicode(self))
        self.is_active = False
        self.save()

    def delete(self, using=None):
        if self.image:
            os.unlink(self.image.path)
        super(AlbumImage, self).delete(using)

    @permalink
    def get_absolute_url(self):
        return 'imagestore:image', (), {'pk': self.id}

    def __unicode__(self):
        return '%s'% self.id


    class Meta:
        ordering = ('order', '-created')
        get_latest_by = "updated"
