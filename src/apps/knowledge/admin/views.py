#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, ListView
import os
from apps.knowledge.models import Knowledge
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, AjaxDetailView, RequestAwareMixin, \
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView, ModelActiveView, AdminRequiredMixin
from .forms import KnowledgeForm, KnowledgeDatatablesBuilder
from utils.db.queryutil import get_object_or_none

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class KnowledgeListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Knowledge
    datatables_builder_class = KnowledgeDatatablesBuilder
    queryset = Knowledge.objects.get_empty_query_set()


class KnowledgeListDatatablesView(AjaxDatatablesView):
    model = Knowledge
    datatables_builder_class = KnowledgeListView.datatables_builder_class
    queryset = Knowledge.active_objects.order_by('-updated')


class KnowledgeCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = Knowledge
    form_class = KnowledgeForm
    form_action_url_name = 'admin:knowledge:knowledge_create'
    template_name = 'knowledge/admin/knowledge.form.inc.html'


class KnowledgeEditView(ModelAwareMixin, AjaxUpdateView):
    model = Knowledge
    form_class = KnowledgeForm
    form_action_url_name = 'admin:knowledge:knowledge_edit'
    template_name = 'knowledge/admin/knowledge.form.inc.html'

    def get_initial(self):
        initial = super(KnowledgeEditView, self).get_initial()
        if self.object:
            initial["content_html"] = self.object.content_html()
        return initial


class KnowledgeUpdateView(AjaxSimpleUpdateView):
    model = Knowledge

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def publish(self, product):
        product.is_published = True

    def cancel(self, product):
        product.is_published = False
