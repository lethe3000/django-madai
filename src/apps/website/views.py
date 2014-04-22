#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from django.template.response import TemplateResponse
from apps.tour.models import Article, Scenery, GuideType

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


def index(request):
    banner_list = Article.objects.banner_articles().all()
    # FIXME: UI design is limited to 8 but we need 10 actually.
    scenery_list = Scenery.active_objects.all()[0: 8]
    article_list = Article.objects.hot_articles().all()[0: 8]
    event_list = Article.objects.event_articles().all()[0: 4]
    return TemplateResponse(request, 'website/index.html', locals())


def legal(request):
    return TemplateResponse(request, 'website/legal.inc.html')


def privacy(request):
    return TemplateResponse(request, 'website/privacy.inc.html')

def aboutus(request):
    return TemplateResponse(request, 'website/aboutus.html')