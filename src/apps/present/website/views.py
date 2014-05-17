#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateResponseMixin, View
from apps.package.models import Package
from django.shortcuts import render_to_response
from django.template import RequestContext


class PresentListView(TemplateResponseMixin, View):
    template_name = 'present/website/present.list.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(locals())