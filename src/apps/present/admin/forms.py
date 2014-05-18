#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.core.urlresolvers import reverse
import os
from django import forms
from apps.present.models import Present, PresentCategory
from apps.common.admin.datatables import DatatablesIdColumn, DatatablesBuilder, DatatablesImageColumn, DatatablesTextColumn, \
    DatatablesBooleanColumn, DatatablesUserChoiceColumn, DatatablesDateTimeColumn, DatatablesColumnActionsRender, \
    DatatablesActionsColumn, DatatablesModelChoiceColumn, DatatablesIntegerColumn

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class PresentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PresentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required col-md-10 limited"

    class Meta:
        model = Present
        fields = ('name', 'desc', 'price', 'image_file')

        widgets = {
        }

    def save(self, commit=False):
        present = super(PresentForm, self).save(commit)
        if not hasattr(present, "creator"):
            present.creator = self.initial['request'].user
        present.save()
        return present


class PresentDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label=u'名称',
                                is_searchable=True)

    image_file = DatatablesImageColumn(label=u'图片')

    price = DatatablesTextColumn(label=u'价值')

    desc = DatatablesTextColumn(label=u'描述',
                                is_searchable=True)

    is_published = DatatablesBooleanColumn((('', u'全部'), (1, u'激活'), (0, u'锁定')),
                                           label='状态',
                                           is_searchable=True,
                                           col_width='5%',
                                           render=(lambda request, model, field_name:
                                                   u'<span class="label label-info"> 启用 </span>' if model.is_published else
                                                   u'<span class="label label-warning"> 草稿 </span>'))

    def actions_render(request, model, field_name):
        action_url_builder = lambda model, action: reverse('admin:present:present_update', kwargs={'pk': model.id, 'action_method': action})

        if model.is_published:
            actions = [{'is_link': False, 'name': 'cancel', 'text': u'取消',
                        'icon': 'icon-unlock', "url": action_url_builder(model, "cancel")}]
        else:
            actions = [{'is_link': False, 'name': 'publish', 'text': u'发布',
                        'icon': 'icon-lock', "url": action_url_builder(model, "publish")}]
        actions.append({'is_link': True, 'name': 'edit', 'text': u'编辑',
                        'icon': 'icon-edit', 'url_name': 'admin:present:present_edit'})
        return DatatablesColumnActionsRender(actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)


class PresentCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PresentCategoryForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required col-md-10 limited"
        self.fields['presents'].widget.attrs['class'] = "required col-md-10 limited"

    class Meta:
        model = PresentCategory
        fields = ('name', 'presents')

        widgets = {
        }

    def save(self, commit=False):
        presentcategory = super(PresentCategoryForm, self).save(commit)
        if not hasattr(presentcategory, "creator"):
            presentcategory.creator = self.initial['request'].user
        presentcategory.save()
        return presentcategory


class PresentCategoryDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label=u'名称',
                                is_searchable=True)

    # presents = DatatablesModelChoiceColumn(label=u'包含的礼品',
    #                                        is_searchable=True,
    #                                        queryset=Present.objects.only('name').all())

    is_published = DatatablesBooleanColumn((('', u'全部'), (1, u'激活'), (0, u'锁定')),
                                           label='状态',
                                           is_searchable=True,
                                           col_width='5%',
                                           render=(lambda request, model, field_name:
                                                   u'<span class="label label-info"> 启用 </span>' if model.is_published else
                                                   u'<span class="label label-warning"> 草稿 </span>'))

    def actions_render(request, model, field_name):
        action_url_builder = lambda model, action: reverse('admin:present:presentcategory_update', kwargs={'pk': model.id, 'action_method': action})

        if model.is_published:
            actions = [{'is_link': False, 'name': 'cancel', 'text': u'取消',
                        'icon': 'icon-unlock', "url": action_url_builder(model, "cancel")}]
        else:
            actions = [{'is_link': False, 'name': 'publish', 'text': u'发布',
                        'icon': 'icon-lock', "url": action_url_builder(model, "publish")}]
        actions.append({'is_link': True, 'name': 'edit', 'text': u'编辑',
                        'icon': 'icon-edit', 'url_name': 'admin:present:presentcategory_edit'})
        return DatatablesColumnActionsRender(actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)