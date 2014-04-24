#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, ListView
import os
from apps.tour.models import Scenery, GuideType, Article
from apps.product.models import Hotel, Flight, Combo
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, AjaxDetailView, RequestAwareMixin,\
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView, ModelActiveView, AdminRequiredMixin
from .forms import HotelForm, FlightForm, HotelDatatablesBuilder, FlightDatatablesBuilder, SceneryDatatablesBuilder, SceneryForm, GuideTypeForm, GuideTypeDatatablesBuilder
from utils.db.queryutil import get_object_or_none

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class HotelListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Hotel
    datatables_builder_class = HotelDatatablesBuilder
    queryset = Hotel.objects.get_empty_query_set()


class HotelListDatatablesView(AjaxDatatablesView):
    model = Hotel
    datatables_builder_class = HotelListView.datatables_builder_class
    queryset = Hotel.active_objects.select_related("creator").order_by('-updated')


class HotelCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = Hotel
    form_class = HotelForm
    form_action_url_name = 'admin:product:hotel_create'
    # template_name = 'tour/admin/article.form.inc.html'
    template_name = 'product/admin/hotel.form.inc.html'

    # def get_initial(self):
        # TODO
        # initial = super(HotelCreateView, self).get_initial()
        # try:
        #     initial["scenery"] = self.request.GET['scenery']
        #     initial["guide_type"] = self.request.GET['guidetype']
        # except KeyError:
        #     pass
        # return initial


class HotelEditView(ModelAwareMixin, AjaxUpdateView):
    model = Hotel
    form_class = HotelForm
    form_action_url_name = 'admin:product:hotel_edit'
    template_name = 'product/admin/hotel.form.inc.html'

    def get_initial(self):
        initial = super(HotelEditView, self).get_initial()
        if self.object:
            initial["content_html"] = self.object.content_html()
        return initial


class HotelDeleteView(ModelActiveView):
    model = Hotel


class HotelPreviewView(ModelAwareMixin, AjaxDetailView):
    model = Hotel
    template_name = 'product/admin/hotel.preview.inc.html'


class HotelUpdateView(AjaxSimpleUpdateView):
    model = Hotel

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def publish(self, product):
        product.is_published = True

    def cancel(self, product):
        product.is_published = False

##################################################
#   Flight 直接复用hotel的代码
##################################################


class FlightListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Flight
    datatables_builder_class = FlightDatatablesBuilder
    queryset = Flight.objects.get_empty_query_set()


class FlightListDatatablesView(AjaxDatatablesView):
    model = Flight
    datatables_builder_class = FlightListView.datatables_builder_class
    queryset = Flight.active_objects.select_related("creator").order_by('-updated')


class FlightCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = Flight
    form_class = FlightForm
    form_action_url_name = 'admin:product:flight_create'
    template_name = 'product/admin/hotel.form.inc.html'


class FlightEditView(ModelAwareMixin, AjaxUpdateView):
    model = Flight
    form_class = FlightForm
    form_action_url_name = 'admin:product:flight_edit'
    template_name = 'product/admin/hotel.form.inc.html'

    def get_initial(self):
        initial = super(FlightEditView, self).get_initial()
        if self.object:
            initial["content_html"] = self.object.content_html()
        return initial


class FlightDeleteView(ModelActiveView):
    model = Flight


class FlightPreviewView(ModelAwareMixin, AjaxDetailView):
    model = Flight
    template_name = 'product/admin/hotel.preview.inc.html'


class FlightUpdateView(AjaxSimpleUpdateView):
    model = Flight

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def publish(self, product):
        product.is_published = True

    def cancel(self, product):
        product.is_published = False


##################################################
#   Scenery
##################################################

class SceneryListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Scenery
    queryset = Scenery.objects.get_empty_query_set()
    datatables_builder_class = SceneryDatatablesBuilder


class SceneryListDatatablesView(AjaxDatatablesView):
    model = Scenery
    datatables_builder_class = SceneryListView.datatables_builder_class
    queryset = Scenery.objects.all()


class SceneryCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = Scenery
    form_class = SceneryForm
    template_name = 'tour/admin/scenery.form.inc.html'


class SceneryEditView(ModelAwareMixin, AdminRequiredMixin, AjaxUpdateView):
    model = Scenery
    form_class = SceneryForm
    template_name = 'tour/admin/scenery.form.inc.html'


class SceneryUpdateView(AjaxSimpleUpdateView):
    model = Scenery

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def lock(self, scenery):
        scenery.is_active = False
        scenery.save()

    def unlock(self, scenery):
        scenery.is_active = True
        scenery.save()


class SceneryDashboardView(ListView):
    #model = GuideType
    template_name = 'tour/admin/scenery.dashboard.inc.html'
    context_object_name = "guidetypes"

    def get_context_data(self, **kwargs):
        context = super(SceneryDashboardView, self).get_context_data(**kwargs)
        context['scenery'] = get_object_or_none(Scenery, id=self.kwargs['pk'])
        return context

    def get_queryset(self):
        return Scenery.objects.guidetypes_with_article(self.kwargs['pk'])

##################################################
#   GuideType
##################################################


class GuideTypeListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AdminRequiredMixin, AjaxListView):
    model = GuideType
    queryset = GuideType.objects.get_empty_query_set()
    datatables_builder_class = GuideTypeDatatablesBuilder


class GuideTypeListDatatablesView(AdminRequiredMixin, AjaxDatatablesView):
    model = GuideType
    datatables_builder_class = GuideTypeListView.datatables_builder_class
    queryset = GuideType.objects.all()


class GuideTypeCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = GuideType
    form_class = GuideTypeForm
    template_name = 'tour/admin/scenery.form.inc.html'


class GuideTypeEditView(ModelAwareMixin, AjaxUpdateView):
    model = GuideType
    form_class = GuideTypeForm
    template_name = 'tour/admin/scenery.form.inc.html'


class GuideTypeUpdateView(AjaxSimpleUpdateView):
    model = GuideType

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def lock(self, guidetype):
        if Article.active_objects.filter(guide_type=guidetype).count():
            return u'不能锁定该资讯类型，已经有景区文章被指定为该类型'
        guidetype.is_active = False
        guidetype.save()

    def unlock(self, guidetype):
        guidetype.is_active = True
        guidetype.save()
