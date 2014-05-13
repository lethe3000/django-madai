#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.generic.base import TemplateResponseMixin, View, RedirectView
from django.views.generic.list import BaseListView
from apps.tour.models import Article, Scenery, GuideType
from apps.hotel.models import Hotel, HotelArticle, InfoType


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
        hotel_list = Hotel.active_objects.all()
        return self.render_to_response(locals())