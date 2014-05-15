#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse
from apps.package.models import Package
from django.shortcuts import render_to_response
from django.template import RequestContext


def searching(request):
    start_address = request.GET['start_address']
    start_date = request.GET['start_date']
    price_min = request.GET['price_min']
    price_max = request.GET['price_max']

    # # TEST CODE # #
    # package = Package.active_objects.all()[0]
    # start_address = u'成都'
    # import datetime
    # start_date = datetime.date(2014, 5, 1)
    # price_min = 1000
    # price_max = 3000
    # # END TEST # #
    packages = Package.active_objects.select_related('hotels', 'flights').filter(
        start_city=start_address,
        price__lt=price_max,
        price__gt=price_min,
        start_date__lt=start_date,
        end_date__gt=start_date)

    if packages.count():
        # FIXME 多个package如何挑选, 暂时选第一个
        package = packages[0]
        return render_to_response('package/website/package.searching.html',
                                  locals(),
                                  context_instance=RequestContext(request))
    else:
        #TODO 无套餐需要个空套餐页面
        return render_to_response('package/website/package.searching.html',
                                  locals(),
                                  context_instance=RequestContext(request))