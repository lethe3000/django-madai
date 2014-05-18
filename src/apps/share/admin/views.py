#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, ListView
import os
from apps.share.models import TravelNote
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, AjaxDetailView, RequestAwareMixin, \
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView, ModelActiveView, AdminRequiredMixin
from .forms import TravelNoteDatatablesBuilder, TravelNoteForm
from utils.db.queryutil import get_object_or_none

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class TravelNoteListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = TravelNote
    datatables_builder_class = TravelNoteDatatablesBuilder
    queryset = TravelNote.objects.get_empty_query_set()


class TravelNoteListDatatablesView(AjaxDatatablesView):
    model = TravelNote
    datatables_builder_class = TravelNoteListView.datatables_builder_class
    queryset = TravelNote.active_objects.order_by('-updated')


class TravelNoteCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = TravelNote
    form_class = TravelNoteForm
    form_action_url_name = 'admin:share:travelnote_create'
    template_name = 'share/admin/travelnote.form.inc.html'


class TravelNoteEditView(ModelAwareMixin, AjaxUpdateView):
    model = TravelNote
    form_class = TravelNoteForm
    form_action_url_name = 'admin:share:travelnote_edit'
    template_name = 'share/admin/travelnote.form.inc.html'

    def get_initial(self):
        initial = super(TravelNoteEditView, self).get_initial()
        if self.object:
            initial["content_html"] = self.object.content_html()
        return initial



# class ArticleDeleteView(ModelActiveView):
#     model = HotelArticle
#     unique_field_on_inactive = 'title'
#
#
# class ArticlePreviewView(ModelAwareMixin, AjaxDetailView):
#     model = HotelArticle
#     template_name = 'hotel/admin/article.preview.inc.html'


# class ArticleHtmlRedirectView(RedirectView):
#     def get_redirect_url(self, pk):
#         article = get_object_or_404(HotelArticle, pk=pk)
#         return article.content_file.url


class TravelNoteUpdateView(AjaxSimpleUpdateView):
    model = TravelNote

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