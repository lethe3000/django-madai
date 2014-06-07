#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from django.template.response import TemplateResponse
from apps.hotel.models import Hotel
from apps.present.models import Present
from apps.share.models import TravelNote

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


def index(request):
    hotels = Hotel.active_objects.order_by('display_order').filter(is_promotion=True, is_published=True)[0: 9]
    hotel_banners = Hotel.active_objects.order_by('display_order').filter(is_banner=True, is_published=True)[0: 3]
    presents = Present.active_objects.order_by('display_order').filter(is_pinned=True, is_published=True)[0:9]
    travel_notes = TravelNote.active_objects.order_by('display_order').filter(is_pinned=True, is_published=True)[0: 9]
    return TemplateResponse(request, 'website/index.html', locals())


def legal(request):
    return TemplateResponse(request, 'website/index.html')


def privacy(request):
    return TemplateResponse(request, 'website/index.html')


def aboutus(request):
    return TemplateResponse(request, 'website/index.html')