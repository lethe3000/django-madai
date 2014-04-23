#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apps.common.models import BaseModel, ActiveDataManager, TimeBaseModel
from django.conf import settings
from django.db import models

# TODO 包括酒店，航班和打包推荐


class Hotel(BaseModel):
    # name, price, address, phone, ...
    pass


class Flight(BaseModel):
    # name, flight_number, time, airway, ...
    pass


class Combo(BaseModel):
    # 打包的hotel和flight
    # name, time, hotel, flight, price, ...
    amount = models.DecimalField(max_digits=16,
                                 decimal_places=2,
                                 verbose_name=u'总价',
                                 default=0.0)

