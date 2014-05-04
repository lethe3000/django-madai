#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.conf import settings
from django.db import models
import os

from apps.account.models import User
from apps.common.models import BaseModel
from utils import random

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


def unique_avatar_name(instance, filename):
    try:
        ext = os.path.splitext(filename)[1].lstrip('.')
    except BaseException:
        ext = "jpg"
    return '%s/avatar_%s' % (settings.MEDIA_IMAGE_PREFIX, random.gen_uuid_filename(ext))


class Customer(User):
    avatar_file = models.ImageField(upload_to=unique_avatar_name,
                                    blank=True,
                                    null=True,
                                    verbose_name=u'头像')

    address = models.CharField(max_length=128,
                               verbose_name=u'来自',
                               blank=True,
                               default='')

    signature = models.CharField(max_length=128,
                                 verbose_name=u'个性签名',
                                 blank=True,
                                 default='')

    updated = models.DateTimeField(verbose_name=u'更新时间',
                                   auto_now=True,
                                   null=True)

    def __init__(self, *args, **kwargs):
        super(Customer, self).__init__(*args, **kwargs)
        self._original_password = self.password
        self.is_password_changed = False

    def updated_timestamp(self):
        return int(self.updated.strftime("%s")) if self.updated else 0

    class Meta:
        verbose_name = u'终端用户'
        verbose_name_plural = verbose_name
        permissions = (
            ("view_customer", "查看终端用户"),
        )

    def avatar_url(self):
        return settings.STATIC_DEFAULT_AVATAR_URL if not self.avatar_file else self.avatar_file.url

    def save(self, *args, **kwargs):
        self.is_password_changed = self._original_password != self.password
        super(Customer, self).save(*args, **kwargs)


class Journal(BaseModel):
    title = models.CharField(max_length=128,
                             verbose_name=u'标题',
                             blank=True,
                             default='')

    content = models.TextField(verbose_name=u'游记内容',
                               blank=True,
                               default='')

    def deactivate(self):
        self.is_active = False
        self.save()

    class Meta:
        verbose_name = u'用户游记'
        get_latest_by = ('updated',)
