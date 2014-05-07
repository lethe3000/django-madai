#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse


def searching(request):
    # TODO 根据条件: 出发地，时间，价格区间来选择package
    return TemplateResponse(request, 'package/website/package.searching.html')