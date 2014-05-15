#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, ListView
import os
from apps.hotel.models import HotelArticle
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, AjaxDetailView, RequestAwareMixin,\
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView, ModelActiveView, AdminRequiredMixin
from apps.hotel.models import Hotel, InfoType
from .forms import ArticleForm, ArticleDatatablesBuilder, HotelDatatablesBuilder, HotelForm, InfoTypeForm, InfoTypeDatatablesBuilder
from utils.db.queryutil import get_object_or_none

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ArticleListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = HotelArticle
    datatables_builder_class = ArticleDatatablesBuilder
    queryset = HotelArticle.objects.get_empty_query_set()


class ArticleListDatatablesView(AjaxDatatablesView):
    model = HotelArticle
    datatables_builder_class = ArticleListView.datatables_builder_class
    queryset = HotelArticle.active_objects.select_related("hotel", "guide_type", "creator").order_by('-updated')


class ArticleCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = HotelArticle
    form_class = ArticleForm
    form_action_url_name = 'admin:hotel:hotelarticle_create'
    template_name = 'hotel/admin/article.form.inc.html'

    def get_initial(self):
        initial = super(ArticleCreateView, self).get_initial()
        try:
            initial["hotel"] = self.request.GET['hotel']
            initial["info_type"] = self.request.GET['infotype']
        except KeyError:
            pass
        return initial

    def get_context_data(self, **kwargs):
        context_data = super(ArticleCreateView, self).get_context_data(**kwargs)
        try:
            infotype = int(self.request.GET['infotype'])
        except KeyError:
            infotype = -1 # no pre-set guidetype
        context_data['editor_max_image_side_length'] = 3000 if infotype == InfoType.INFO_TYPE_MAP else 640
        return context_data


class ArticleEditView(ModelAwareMixin, AjaxUpdateView):
    model = HotelArticle
    form_class = ArticleForm
    form_action_url_name = 'admin:hotel:hotelarticle_edit'
    template_name = 'hotel/admin/article.form.inc.html'

    def get_initial(self):
        initial = super(ArticleEditView, self).get_initial()
        if self.object:
            initial["content_html"] = self.object.content_html()
        return initial

    def get_context_data(self, **kwargs):
        context_data = super(ArticleEditView, self).get_context_data(**kwargs)
        context_data['editor_max_image_side_length'] = 3000 if self.object.info_type.id == InfoType.INFO_TYPE_MAP else 640
        return context_data


class ArticleDeleteView(ModelActiveView):
    model = HotelArticle
    unique_field_on_inactive = 'title'


class ArticlePreviewView(ModelAwareMixin, AjaxDetailView):
    model = HotelArticle
    template_name = 'hotel/admin/article.preview.inc.html'


class ArticleHtmlRedirectView(RedirectView):
    def get_redirect_url(self, pk):
        article = get_object_or_404(HotelArticle, pk=pk)
        return article.content_file.url


class ArticleUpdateView(AjaxSimpleUpdateView):
    model = HotelArticle

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
#   Hotel
##################################################


class HotelListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Hotel
    queryset = Hotel.objects.get_empty_query_set()
    datatables_builder_class = HotelDatatablesBuilder


class HotelListDatatablesView(AjaxDatatablesView):
    model = Hotel
    datatables_builder_class = HotelListView.datatables_builder_class
    queryset = Hotel.objects.all()


class HotelCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = Hotel
    form_class = HotelForm
    template_name = 'hotel/admin/hotel.form.inc.html'

    def get_context_data(self, **kwargs):
        context_data = super(HotelCreateView, self).get_context_data(**kwargs)
        context_data['editor_max_image_side_length'] = 3000
        return context_data


class HotelEditView(ModelAwareMixin, AjaxUpdateView):
    model = Hotel
    form_class = HotelForm
    template_name = 'hotel/admin/hotel.form.inc.html'

    def get_initial(self):
        initial = super(HotelEditView, self).get_initial()
        if self.object:
            initial["images_html"] = self.object.images_html()
        return initial

    def get_context_data(self, **kwargs):
        context_data = super(HotelEditView, self).get_context_data(**kwargs)
        context_data['editor_max_image_side_length'] = 3000
        return context_data

class HotelUpdateView(AjaxSimpleUpdateView):
    model = Hotel

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def cancel(self, hotel):
        hotel.is_published = False

    def publish(self, hotel):
        hotel.is_published = True


class HotelDashboardView(ListView):
    template_name = 'hotel/admin/hotel.dashboard.inc.html'
    context_object_name = "infotypes"

    def get_context_data(self, **kwargs):
        context = super(HotelDashboardView, self).get_context_data(**kwargs)
        context['hotel'] = get_object_or_none(Hotel, id=self.kwargs['pk'])
        return context

    def get_queryset(self):
        return Hotel.objects.infotypes_with_article(self.kwargs['pk'])

##################################################
#   InfoType
##################################################


class InfoTypeListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = InfoType
    queryset = InfoType.objects.get_empty_query_set()
    datatables_builder_class = InfoTypeDatatablesBuilder


class InfoTypeListDatatablesView(AjaxDatatablesView):
    model = InfoType
    datatables_builder_class = InfoTypeListView.datatables_builder_class
    queryset = InfoType.objects.all()


class InfoTypeCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = InfoType
    form_class = InfoTypeForm
    template_name = 'hotel/admin/hotel.form.inc.html'


class InfoTypeEditView(ModelAwareMixin, AjaxUpdateView):
    model = InfoType
    form_class = InfoTypeForm
    template_name = 'hotel/admin/hotel.form.inc.html'


class InfoTypeUpdateView(AjaxSimpleUpdateView):
    model = InfoType

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def lock(self, infotype):
        if HotelArticle.active_objects.filter(info_type=infotype).count():
            return u'不能锁定该资讯类型，已经有酒店文章被指定为该类型'
        infotype.is_active = False
        infotype.save()

    def unlock(self, infotype):
        infotype.is_active = True
        infotype.save()
