#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from django.views.generic.base import TemplateResponseMixin, View
from apps.common.admin.views import HttpResponseJson
from apps.flight.models import Flight, InfoType


class FlightDetailView(TemplateResponseMixin, View):
    template_name = 'flight/website/flight.html'

    def get(self, request, *args, **kwargs):
        flight = Flight.active_objects.get(pk=self.kwargs['pk'])
        # FIXME 只取发布的article不为0的info_type
        info_type_list = list(
            InfoType.active_objects.filter(articles__flight=flight) \
                .only('name', 'image_file', 'summary') \
                .distinct()
        )
        articles = []
        for info in info_type_list:
            latest_article = info.articles.latest_flight_article(flight.id, info.id)
            if latest_article:
                articles.append(latest_article)
            else:
                info_type_list.remove(info)
        return self.render_to_response(locals())


class FlightListView(TemplateResponseMixin, View):
    template_name = 'flight/website/flight.list.html'

    def get(self, request, *args, **kwargs):
        cursor = request.GET.get('cursor')
        if cursor:
            cursor = datetime.fromtimestamp(int(cursor))
            flights = Flight.active_objects.filter(updated__lt=cursor, is_published=True).order_by("-display_order").order_by('-updated')
            flight_json_list = []
            for flight in flights:
                flight_json_list.append({"id": flight.id,
                                         "img": flight.image_url(),
                                         "name": flight.name,
                                         "summary": flight.summary,
                                         "price": flight.price,
                                         "updated": flight.updated_timestamp()})
            return HttpResponseJson(result=flight_json_list)
        else:
            return self.render_to_response(locals())