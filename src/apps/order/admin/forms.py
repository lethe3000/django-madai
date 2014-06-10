#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.core.urlresolvers import reverse
import os
from django import forms
from apps.package.models import Package
from apps.order.models import Order
from apps.common.admin.datatables import DatatablesIdColumn, DatatablesBuilder, DatatablesImageColumn, DatatablesTextColumn, \
    DatatablesBooleanColumn, DatatablesUserChoiceColumn, DatatablesDateTimeColumn, DatatablesColumnActionsRender, \
    DatatablesActionsColumn, DatatablesModelChoiceColumn, DatatablesIntegerColumn, DatatablesChoiceColumn

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class OrderDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    display_id = DatatablesTextColumn(label=u"订单号",
                                      is_searchable=True)

    package = DatatablesTextColumn(label=u'套餐',
                                   is_searchable=True)

    hotel = DatatablesTextColumn(label=u'酒店',
                                 is_searchable=True)

    flight = DatatablesTextColumn(label=u'航班',
                                  is_searchable=True)

    customer_name = DatatablesTextColumn(label=u'客户名',
                                         is_searchable=True)

    phone = DatatablesTextColumn(label=u'联系电话',
                                 is_searchable=True)

    start_address = DatatablesTextColumn(label=u'出发地址',
                                         is_searchable=True)

    start_date = DatatablesDateTimeColumn(label=u'预期出发时间')

    notes = DatatablesTextColumn(label=u'客户留言',
                                 is_searchable=True)

    status = DatatablesChoiceColumn(Order.ORDER_STATUS_CODES,
                                    label=u'状态',
                                    is_searchable=True)

    def actions_render(request, model, field_name):
        actions = [{'is_link': True,  'name': 'edit', 'text': u'编辑', 'icon': 'icon-edit'},
                   {'is_link': False, 'name': 'delete', 'text': u'删除', 'icon': 'icon-remove'},]
        next_action = model.next_action_for_admin()
        if next_action:
            actions.append({'is_link': False, 'name': 'order_update', 'text': next_action['label'], 'icon': 'icon-money',
                            'url': reverse('admin:order:order_update', kwargs={'pk': model.id, 'action_method': next_action['next']})})

        return DatatablesColumnActionsRender(actions=actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)


class OrderForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(OrderForm, self).__init__(*args, **kwargs)
    #     self.fields['name'].widget.attrs['class'] = "required col-md-10 limited"
    #     self.fields['summary'].widget.attrs['class'] = "col-md-10 limited"

    class Meta:
        model = Order
        fields = ('package', 'hotel', 'flight', 'customer_name', 'phone', 'start_address', 'start_date', 'notes')
