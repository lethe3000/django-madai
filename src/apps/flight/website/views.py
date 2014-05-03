#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateResponseMixin, View


class FlightDetailView(TemplateResponseMixin, View):
    template_name = 'flight/website/flight.html'

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        return self.render_to_response(locals())