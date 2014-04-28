#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.generic.base import TemplateResponseMixin, View, RedirectView
from django.views.generic.list import BaseListView
from apps.tour.models import Article, Scenery, GuideType


class HotelDetailView(TemplateResponseMixin, View):
    template_name = 'hotel/website/hotel.html'

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        return self.render_to_response(locals())