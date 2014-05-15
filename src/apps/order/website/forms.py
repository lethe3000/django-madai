#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import AnonymousUser
from apps.flight.models import Flight
from apps.hotel.models import Hotel
from apps.order.models import Order
from apps.package.models import Package


class OrderForm(forms.Form):

    customer_name = forms.CharField(label=u'姓名',
                                    max_length=10,
                                    help_text=u'必填.')

    phone = forms.RegexField(label=u'手机号',
                            max_length=11,
                            help_text=u'必填.',
                            regex="^1[\d]{10}$",
                            error_message=u"请输入正确的手机号")

    start_address = forms.CharField(label=u'出发地址',
                                    max_length=64,
                                    help_text=u'必填.')

    start_date = forms.DateTimeField(label=u'期望出发时间')

    def save(self, request):
        package_id = request.POST['package_id']
        package = Package.objects.get(id=package_id)
        if not isinstance(request.user, AnonymousUser):
            customer = request.user.customer
        else:
            customer = None
        hotel_id = request.POST['hotel_id']
        hotel = Hotel.objects.get(id=hotel_id)
        flight_id = request.POST['flight_id']
        flight = Flight.objects.get(id=flight_id)
        order = Order(package=package,
                      hotel=hotel,
                      flight=flight,
                      customer=customer,
                      customer_name=self.cleaned_data['customer_name'],
                      phone=self.cleaned_data['phone'],
                      start_address=self.cleaned_data['start_address'],
                      start_date=self.cleaned_data['start_date'],
                      )
        order.save()
        return order