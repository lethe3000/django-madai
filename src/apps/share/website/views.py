#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from django.views.generic.base import TemplateResponseMixin, View
from apps.common.admin.views import HttpResponseJson
from apps.hotel.models import Hotel, InfoType
from apps.share.models import TravelNote


class TravelNoteDetailView(TemplateResponseMixin, View):
    template_name = 'share/website/travelnote.html'

    def get(self, request, *args, **kwargs):
        note = TravelNote.active_objects.get(pk=self.kwargs['pk'])
        return self.render_to_response(locals())