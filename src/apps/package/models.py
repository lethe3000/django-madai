#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from utils import pretty_price
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

    PRICE_CHOICES = (
        ('20000-25000', '20000-25000'),
        ('25000-30000', '25000-30000'),
        ('30000-35000', '30000-35000'),
        ('35000-40000', '35000-40000'),
        ('40000+', '40000+'),
    )

    price = models.CharField(max_length=32, choices=PRICE_CHOICES,
                             default='20000-25000',
                             blank=True,
                             verbose_name=u'套餐价格')

    is_published = models.BooleanField(default=False,
                                       verbose_name=u'是否已发布')

    # 关联的推荐酒店和航线
    hotels = models.ManyToManyField(Hotel,
                                    verbose_name=u'酒店',
                                    related_name='package')

    flights = models.ManyToManyField(Flight,
                                     verbose_name=u'航线',
                                     related_name='package')

    # 查询条件
    start_date = models.DateTimeField(verbose_name=u'起始有效时间')

    end_date = models.DateTimeField(verbose_name=u'结束有效时间',
                                    auto_now_add=False,
                                    blank=True)

    CITY_CHOICES = (
        (u'成都', u'成都'),
        (u'重庆', u'重庆'),
        (u'上海', u'上海'),
        (u'北京', u'北京'),
        (u'香港', u'香港'),
    )
    start_city = models.CharField(max_length=32,
                                  verbose_name=u'出发城市',
                                  choices=CITY_CHOICES, default=u'成都')

    active_objects = ActiveDataManager()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u"套餐"
        get_latest_by = "updated"

    STATUS_OK = 0
    STATUS_DELETE = -1

    def status(self):
        return self.STATUS_OK if self.is_published and self.is_active else self.STATUS_DELETE

    def get_pretty_price(self):
        return pretty_price(self.price)

    def __unicode__(self):
        return self.title
