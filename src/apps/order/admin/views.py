#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, AjaxDetailView, RequestAwareMixin, \
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView, ModelActiveView, AdminRequiredMixin
from apps.order.models import Order, OrderHistory
from .forms import OrderDatatablesBuilder, OrderForm

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class OrderListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Order
    datatables_builder_class = OrderDatatablesBuilder
    queryset = Order.objects.get_empty_query_set()

    def get_context_data(self, **kwargs):
        context_data = super(OrderListView, self).get_context_data(**kwargs)
        context_data['create_url'] = ''
        return context_data


class OrderListDatatablesView(AjaxDatatablesView):
    model = Order
    datatables_builder_class = OrderListView.datatables_builder_class
    queryset = Order.objects.order_by('-updated')


class OrderCreateView(CreateAPIView):
    """
    """
    model = Order

    def post(self, request, *args, **kwargs):
        # TODO create order
        print 'create order'
        order = Order()
        if request.user.is_active:
            order.customer = request.user
            order.customer_name = order.customer.name
            order.phone = order.customer.phone
        else:
            order.customer = None
            order.customer_name = request.DATA.get('customer_name', '')
            order.phone = request.DATA.get('phone', '')
        order.package = request.DATA.get('package', None)
        order.hotel = request.DATA.get('hotel', None)
        order.flight = request.DATA.get('flight', None)
        order.start_address = request.DATA.get('start_address', '')
        import datetime
        order.start_date = request.DATA.get('start_date', datetime.datetime.now())
        order.notes = request.DATA.get('notes', '')
        order.save()
        return Response(data={'msg': 'success'})


class OrderUpdateView(AjaxSimpleUpdateView):
    model = Order

    def update(self, obj):
        new_status = int(self.kwargs['action_method'])
        obj.set_status(new_status, self.request.user)
        try:
            obj.save()
        except Exception, e:
            return 'update order status error: %s' % e


class OrderEditView(ModelAwareMixin, AjaxUpdateView):
    model = Order
    form_class = OrderForm
    form_action_url_name = 'admin:order:order_edit'
    template_name = 'order/admin/order.form.inc.html'


class OrderDeleteView(ModelActiveView):
    model = Order
