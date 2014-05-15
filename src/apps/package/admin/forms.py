#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.core.urlresolvers import reverse
import os
from django import forms
from apps.package.models import Package
from apps.common.admin.datatables import DatatablesIdColumn, DatatablesBuilder, DatatablesImageColumn, DatatablesTextColumn, \
    DatatablesBooleanColumn, DatatablesUserChoiceColumn, DatatablesDateTimeColumn, DatatablesColumnActionsRender, \
    DatatablesActionsColumn, DatatablesModelChoiceColumn, DatatablesIntegerColumn

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class PackageForm(forms.ModelForm):

    start_date = forms.DateTimeField(label=u"起始有效时间")

    end_date = forms.DateTimeField(label=u"结束有效时间")

    def __init__(self, *args, **kwargs):
        super(PackageForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required col-md-10 limited"
        self.fields['summary'].widget.attrs['class'] = "col-md-10 limited"

    class Meta:
        model = Package
        fields = ('name', 'start_date', 'end_date', 'start_city', 'title', 'summary', 'desc', 'price', 'hotels', 'flights')

        widgets = {
        }

    def save(self, commit=False):
        package = super(PackageForm, self).save(commit)
        if not hasattr(package, "creator"):
            package.creator = self.initial['request'].user
        package.save()
        return package


class PackageDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label=u'名称',
                                is_searchable=True)

    start_date = DatatablesDateTimeColumn(label=u'起始有效时间')

    end_date = DatatablesDateTimeColumn(label=u'结束有效时间')

    start_city = DatatablesTextColumn(label=u'出发城市')

    price = DatatablesUserChoiceColumn(label=u'价格')

    summary = DatatablesTextColumn(label=u'简介',)

    is_active = DatatablesBooleanColumn((('', u'全部'), (1, u'激活'), (0, u'锁定')),
                                        label='状态',
                                        is_searchable=True,
                                        col_width='5%',
                                        render=(lambda request, model, field_name:
                                                u'<span class="label label-info"> 启用 </span>' if model.is_published else
                                                u'<span class="label label-warning"> 禁用 </span>'))

    def actions_render(request, model, field_name):
        action_url_builder = lambda model, action: reverse('admin:package:package_update', kwargs={'pk': model.id, 'action_method': action})

        if model.is_published:
            actions = [{'is_link': False, 'name': 'cancel', 'text': u'撤销',
                        'icon': 'icon-unlock', "url": action_url_builder(model, "cancel")}]
        else:
            actions = [{'is_link': False, 'name': 'publish', 'text': u'发布',
                        'icon': 'icon-lock', "url": action_url_builder(model, "publish")}]
        actions.append({'is_link': True, 'name': 'edit', 'text': u'编辑',
                        'icon': 'icon-edit', 'url_name': 'admin:package:package_edit'})
        return DatatablesColumnActionsRender(actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)