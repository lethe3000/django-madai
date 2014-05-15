#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from django.template.response import TemplateResponse
from apps.flight.models import Flight
from apps.hotel.models import Hotel
from apps.package.models import Package
from apps.tour.models import Article, Scenery, GuideType

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


def index(request):
    hotels = Hotel.active_objects.order_by('-updated').all()[0: 9]
    flights = Flight.active_objects.order_by('-updated').all()[0: 9]
    # packages = Package.active_objects.order_by('-updated').all()[0: 3]
    return TemplateResponse(request, 'website/index.html', locals())


def legal(request):
    return TemplateResponse(request, 'website/index.html')


def privacy(request):
    return TemplateResponse(request, 'website/index.html')


def aboutus(request):
    return TemplateResponse(request, 'website/index.html')