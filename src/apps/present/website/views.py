#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateResponseMixin, View
from apps.present.models import PresentCategory, Present
from django.shortcuts import render_to_response
from django.template import RequestContext


class PresentListView(TemplateResponseMixin, View):
    template_name = 'present/website/present.list.html'

    def get(self, request, *args, **kwargs):
        present_category = PresentCategory.active_objects.order_by("-display_order").filter(is_published=True)
        return self.render_to_response(locals())


class PresentDetailView(TemplateResponseMixin, View):
    template_name = 'present/website/present.html'

    def get(self, request, *args, **kwargs):
        present = Present.active_objects.get(pk=self.kwargs['pk'])
        return self.render_to_response(locals())
