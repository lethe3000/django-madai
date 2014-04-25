#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse


def searching(request):
    return TemplateResponse(request, 'package/website/package.searching.html')