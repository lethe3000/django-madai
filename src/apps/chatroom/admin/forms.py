#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from apps.common.admin.datatables import DatatablesBuilder, DatatablesIdColumn, DatatablesTextColumn, DatatablesDateTimeColumn, DatatablesUserChoiceColumn, DatatablesColumnActionsRender, DatatablesActionsColumn


class ChatroomDatatablesBuilder(DatatablesBuilder):
    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label=u'聊天室名称',
                                is_searchable=True)

    owner = DatatablesTextColumn(label='所有者',
                                 is_sortable=True)

    description = DatatablesTextColumn(label=u'描述')

    updated = DatatablesDateTimeColumn(label='修改时间')

    def actions_render(request, model, field_name):
        action_url_builder = lambda model, action: reverse('admin:chatroom:chatroom_update', kwargs={'pk': model.id, 'action_method': action})
        actions = [
                   {'is_link': True, 'css_class': 'btn-info', 'name': 'detail', 'text': u'详情', 'icon': 'icon-edit'},
                   {'is_link': False, 'css_class': 'btn-warning', 'name': 'delete',
                    'url': action_url_builder(model, 'delete'), 'text': u'删除', 'icon': 'icon-remove'}]

        return DatatablesColumnActionsRender(actions=actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)