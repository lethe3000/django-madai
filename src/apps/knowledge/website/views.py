#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from django.views.generic.base import TemplateResponseMixin, View
from apps.common.admin.views import HttpResponseJson
from apps.hotel.models import Hotel, InfoType
from apps.knowledge.models import Knowledge
from apps.share.models import TravelNote


class KnowledgeDetailView(TemplateResponseMixin, View):
    template_name = 'knowledge/website/knowledge.html'

    def get(self, request, *args, **kwargs):
        knowledge = Knowledge.active_objects.get(pk=self.kwargs['pk'])
        return self.render_to_response(locals())


class KnowledgeListView(TemplateResponseMixin, View):
    template_name = 'knowledge/website/knowledge.list.html'

    def get(self, request, *args, **kwargs):
        knowledge_list = Knowledge.active_objects.order_by("-display_order").filter(is_published=True)
        return self.render_to_response(locals())