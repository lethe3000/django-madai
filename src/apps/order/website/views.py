#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.generic import View
from datetime import datetime
from apps.common import exceptions
from apps.common.admin.views import HttpResponseJson
from apps.order.website.forms import OrderForm


class OrderCreateView(View):

    def post(self, request, *args, **kwargs):
        form = OrderForm(data=request.POST, request=request)
        if form.is_valid():
            order = form.save(request)
            order.display_id = "XMD%s%d" % (datetime.now().strftime('%Y%m%d'), order.pk)
            order.save()
            response_data = exceptions.build_success_response_result()
            response_data['order'] = {'id': order.id}
            return HttpResponseJson(response_data, self.request);
        else:
            raise exceptions.AjaxValidateFormFailed(errors=form.errors)
