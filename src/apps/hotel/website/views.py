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
        page = int(request.GET.get('page', 1))
        prev_page = page - 1 if page > 1 else 1
        page_size = 6
        filter = request.GET.get('filter')
        query_set = Hotel.active_objects if not filter or filter == 'all' else Hotel.active_objects.filter(short_index=filter)
        hotels = query_set.order_by('-updated')[(page - 1) * page_size: page * page_size]
        total_count = query_set.count()
        page_range = [x + 1 for x in range(0, ((total_count - 1) / page_size) + 1)]
        page_range = page_range if page_range else [1]
        next_page = page + 1 if page + 1 <= len(page_range) else page
        first_letters = Hotel.objects.raw('''
            select id, short_index as short_index from hotel_hotel where is_published = 1 group by short_index order by short_index;
        ''');
        return self.render_to_response(locals())


class HotelPromotionListView(HotelListView):
    # TODO
    # hotels = Hotel.active_objects.filter(updated__lt=cursor, is_promotion=True).order_by('-updated')
    # summary字段显示hotel.articles.filter(infotype=promotion)
    pass