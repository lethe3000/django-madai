#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from django.db import models
from django.contrib.auth import get_user_model
from apps.customer.models import Customer
from apps.product.models import Hotel, Flight, Combo
from apps.common.models import BaseModel, ActiveDataManager, TimeBaseModel

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class Order(TimeBaseModel):
    combo = models.ForeignKey(Combo,
                              verbose_name=u'套餐名')

    # 出发地址可能是来自combo，也可能直接读取用户的信息，这里作最终判定的地址
    start_address = models.CharField(verbose_name=u'出发地址',
                                     max_length=255,
                                     default="",
                                     blank=True)

    # TODO: should refer to real payment instead of a string
    payment = models.CharField(verbose_name=u'付款方式',
                               max_length=100,
                               default="",
                               blank=True)

    creator = models.ForeignKey(Customer,
                                verbose_name=u'创建人',
                                related_name='+')

    notes = models.CharField(verbose_name=u'留言',
                             max_length=256,
                             default="",
                             blank=True)

    ORDER_STATUS_CANCEL = -1
    ORDER_STATUS_DRAFT = 0
    ORDER_STATUS_PAID = 1
    ORDER_STATUS_COMPLETED = 2
    ORDER_STATUS_CODES = (
        (ORDER_STATUS_CANCEL, u'已撤销'),
        (ORDER_STATUS_DRAFT, u'未支付'),
        (ORDER_STATUS_PAID, u'已付款'),
        (ORDER_STATUS_COMPLETED, u'已完成'),
    )
    # the action transitions for customer
    ORDER_STATUS_CUSTOMER_NEXT_ACTIONS = {
        ORDER_STATUS_CANCEL: {},
        ORDER_STATUS_DRAFT: {'next': ORDER_STATUS_PAID, 'label': u'去付款', 'active': True},
        ORDER_STATUS_PAID: {'next': ORDER_STATUS_COMPLETED, 'label': u'完成订单', 'active': False},
        ORDER_STATUS_COMPLETED: {},
        }

    # the action transitions for admin
    ORDER_STATUS_ADMIN_NEXT_ACTIONS = {
        ORDER_STATUS_CANCEL: {},
        ORDER_STATUS_DRAFT: {},
        ORDER_STATUS_PAID: {'next': ORDER_STATUS_COMPLETED, 'label': u'完成订单'},
        ORDER_STATUS_COMPLETED: {},
        }

    # TODO: how about "return"?
    status = models.IntegerField(default=ORDER_STATUS_DRAFT,
                                 choices=ORDER_STATUS_CODES,
                                 verbose_name=u'状态')

    def next_action_for_customer(self):
        return self.ORDER_STATUS_CUSTOMER_NEXT_ACTIONS.get(self.status)

    def next_action_for_admin(self):
        return self.ORDER_STATUS_ADMIN_NEXT_ACTIONS.get(self.status)

    def cancel_action(self):
        return {'next': self.ORDER_STATUS_CANCEL,
                'label': u'取消订单',
                'active': True} if self.status == self.ORDER_STATUS_DRAFT else {}

    def sku_text_list(self):
        return [order_sku.display_text() for order_sku in self.ordersku_set.all()]

    def order_no(self):
        return "%.7d" % self.id

    def is_complete(self):
        return self.status in {self.ORDER_STATUS_CANCEL, self.ORDER_STATUS_COMPLETED}

    def set_status(self, new_status, actor):
        # A order could be set to cancel status only when the order is not paid yet.
        if new_status == Order.ORDER_STATUS_CANCEL and self.status != self.ORDER_STATUS_DRAFT:
            return False
            # check the new status is transited with given rules
        next_action = self.next_action_for_customer()
        if actor.is_staff:
            next_action = self.next_action_for_admin()
        if not next_action or next_action['next'] != new_status:
            return False

        if self.status != new_status:
            self.status = new_status
            # TODO orderhistory
            # post_order_status_changed.send(Order, instance=self, new_status=new_status, actor=actor)
            return True
        return False

    def __unicode__(self):
        return self.order_no()

    class Meta:
        verbose_name = u'订单'
        verbose_name_plural = verbose_name
        ordering = ('-created',)


class OrderHistory(models.Model):
    order = models.ForeignKey(Order,
                              verbose_name=u'订单')

    created = models.DateTimeField(verbose_name=u'创建时间',
                                   auto_now_add=True)

    creator = models.ForeignKey(get_user_model(),
                                verbose_name=u'创建者', )

    status = models.IntegerField(default=Order.ORDER_STATUS_DRAFT,
                                 choices=Order.ORDER_STATUS_CODES,
                                 verbose_name=u'状态')

    def __unicode__(self):
        return "%s-%s" % (unicode(self.order), dict(Order.ORDER_STATUS_CODES)[self.status])

    class Meta:
        verbose_name = u'订单历史'
        verbose_name_plural = verbose_name
        ordering = ('-created',)
        permissions = (('view_order', u'查看订单'),)

