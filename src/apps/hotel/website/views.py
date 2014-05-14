#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from django.views.generic.base import TemplateResponseMixin, View
from apps.common.admin.views import HttpResponseJson
from apps.hotel.models import Hotel, InfoType


class HotelDetailView(TemplateResponseMixin, View):
    template_name = 'hotel/website/hotel.html'

    def get(self, request, *args, **kwargs):
        hotel = Hotel.active_objects.get(pk=self.kwargs['pk'])
        # FIXME 只取发布的article不为0的info_type
        info_type_list = list(
            InfoType.active_objects.filter(articles__hotel=hotel)\
            .only('name', 'image_file', 'summary')\
            .distinct()
        )
        articles = []
        for info in info_type_list:
            latest_article = info.articles.latest_hotel_article(hotel.id, info.id)
            if latest_article:
                articles.append(latest_article)
            else:
                info_type_list.remove(info)
        return self.render_to_response(locals())


class HotelListView(TemplateResponseMixin, View):
    template_name = 'hotel/website/hotel.list.html'

    def get(self, request, *args, **kwargs):
        cursor = request.GET.get('cursor')
        if cursor:
            cursor = datetime.fromtimestamp(int(cursor))
            hotels = Hotel.active_objects.filter(updated__lt=cursor).order_by('-updated')
            hotel_json_list = []
            for hotel in hotels:
                hotel_json_list.append({"id": hotel.id,
                                        "img": hotel.image_url(),
                                        "name": hotel.name,
                                        "summary": hotel.summary,
                                        "price": hotel.price,
                                        "updated": hotel.updated_timestamp()})
            return HttpResponseJson(result=hotel_json_list)
        else:
            return self.render_to_response(locals())