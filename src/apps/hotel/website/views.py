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
        info_type_list = InfoType.active_objects.filter(articles__hotel=hotel)\
            .only('name', 'image_file', 'summary')\
            .distinct()
        articles = []
        for info in info_type_list:
            articles.append(info.articles.latest_article(hotel.id, info.id))
        return self.render_to_response(locals())