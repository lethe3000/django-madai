#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apps.chatroom.admin.forms import ChatroomDatatablesBuilder
from apps.chatroom.models import Chatroom
from apps.common.admin.views import NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView, AjaxDatatablesView, AjaxSimpleUpdateView, ModelDetailView


class ChatroomListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Chatroom
    datatables_builder_class = ChatroomDatatablesBuilder
    queryset = Chatroom.objects.get_empty_query_set()


class ChatroomListDatatablesView(AjaxDatatablesView):
    model = Chatroom
    datatables_builder_class = ChatroomListView.datatables_builder_class
    queryset = Chatroom.active_objects.order_by('-updated')


class ChatroomUpdateView(AjaxSimpleUpdateView):
    model = Chatroom

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def delete(self, chatroom):
        chatroom.is_active = False


class ChatroomDetailView(ModelDetailView):
    model = Chatroom
    template_name = 'chatroom/admin/chatroom.detail.html'