#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import View, TemplateView
import os
from apps.common import exceptions
from apps.common.admin.views import AdminRequiredMixin, HttpResponseJson
from apps.thirdparty.forms import WebCameraForm, Guide360Form

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class WebCameraView(AdminRequiredMixin, TemplateView):
    template_name = 'thirdparty/form.inc.html'

    def get_context_data(self, **kwargs):
        context = super(WebCameraView, self).get_context_data(**kwargs)
        context['page_title'] = '全球眼'
        context['form_id'] = 'webcamera_form'
        context['form_action'] = reverse("admin:thirdparty:webcamera")
        context['resource_link'] = settings.THIRDPARTY_WEBCAMERA_URL
        data = "{}"
        try:
            with open(settings.THIRDPARTY_WEBCAMERA_FILE, 'r') as f:
                data = f.read()
        except IOError as e:
            pass
        context['form'] = WebCameraForm(initial={'data': json.dumps(json.loads(data.decode("utf-8")), indent=2, ensure_ascii=False)})
        return context

    def post(self, request, *args, **kwargs):
        form = WebCameraForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseJson(exceptions.build_success_response_result(), request)
        raise exceptions.AjaxValidateFormFailed(errors=form.errors)


class Guide360View(AdminRequiredMixin, TemplateView):
    template_name = 'thirdparty/form.inc.html'

    def get_context_data(self, **kwargs):
        context = super(Guide360View, self).get_context_data(**kwargs)
        context['page_title'] = '全景360'
        context['form_id'] = 'guide360_form'
        context['resource_link'] = settings.THIRDPARTY_GUIDE360_URL
        data = "{}"
        try:
            with open(settings.THIRDPARTY_GUIDE360_FILE, 'r') as f:
                data = f.read()
        except IOError as e:
            pass
        context['form'] = Guide360Form(initial={'data': json.dumps(json.loads(data.decode("utf-8")), indent=2, ensure_ascii=False)})
        return context
