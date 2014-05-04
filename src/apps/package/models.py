#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from apps.common.models import BaseModel, ActiveDataManager
from apps.hotel.models import Hotel
from apps.flight.models import Flight


class Package(BaseModel):
    name = models.CharField(max_length=128,
                            verbose_name=u'套餐名',
                            unique=True)

    # 基本展现信息
    title = models.CharField(max_length=128,
                             verbose_name=u'标题',
                             unique=True)

    summary = models.CharField(max_length=128,
                               verbose_name=u'简介',
                               default="",
                               blank=True)

    desc = models.TextField(verbose_name=u'描述',
                            default="",
                            blank=True)

    price = models.IntegerField(verbose_name=u'套餐价格',
                                default=0)

    is_published = models.BooleanField(default=False,
                                       verbose_name=u'是否已发布')

    # 关联的推荐酒店和航线
    hotels = models.ManyToManyField(Hotel,
                                    verbose_name=u'酒店',
                                    related_name='combo')

    flights = models.ManyToManyField(Flight,
                                     verbose_name=u'航线',
                                     related_name='combo')

    active_objects = ActiveDataManager()

    def __unicode__(self):
        return self.title

    STATUS_OK = 0
    STATUS_DELETE = -1

    def status(self):
        return self.STATUS_OK if self.is_published and self.is_active else self.STATUS_DELETE

    def __unicode__(self):
        return self.title