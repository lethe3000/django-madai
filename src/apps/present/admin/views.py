#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, AjaxDetailView, RequestAwareMixin, \
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView, ModelActiveView, AdminRequiredMixin
from apps.present.models import Present, PresentCategory
from .forms import PresentCategoryForm, PresentCategoryDatatablesBuilder, PresentForm, PresentDatatablesBuilder

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class PresentListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Present
    datatables_builder_class = PresentDatatablesBuilder
    queryset = Present.active_objects.get_empty_query_set()


class PresentListDatatablesView(AjaxDatatablesView):
    model = Present
    datatables_builder_class = PresentListView.datatables_builder_class
    queryset = Present.active_objects.all()


class PresentCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = Present
    form_class = PresentForm
    template_name = 'present/admin/present.form.inc.html'


class PresentEditView(ModelAwareMixin, AjaxUpdateView):
    model = Present
    form_class = PresentForm
    form_action_url_name = 'admin:present:present_edit'
    template_name = 'present/admin/present.form.inc.html'


class PresentDeleteView(ModelActiveView):
    model = Present


class PresentUpdateView(AjaxSimpleUpdateView):
    model = Present

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def publish(self, present):
        present.is_published = True

    def cancel(self, present):
        present.is_published = False


######### category
class PresentCategoryListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = PresentCategory
    datatables_builder_class = PresentCategoryDatatablesBuilder
    queryset = PresentCategory.active_objects.get_empty_query_set()


class PresentCategoryListDatatablesView(AjaxDatatablesView):
    model = PresentCategory
    datatables_builder_class = PresentCategoryListView.datatables_builder_class
    queryset = PresentCategory.active_objects.all()


class PresentCategoryCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = PresentCategory
    form_class = PresentCategoryForm
    template_name = 'present/admin/present.form.inc.html'


class PresentCategoryEditView(ModelAwareMixin, AjaxUpdateView):
    model = PresentCategory
    form_class = PresentCategoryForm
    form_action_url_name = 'admin:present:presentcategory_edit'
    template_name = 'present/admin/present.form.inc.html'


class PresentCategoryDeleteView(ModelActiveView):
    model = PresentCategory


class PresentCategoryUpdateView(AjaxSimpleUpdateView):
    model = PresentCategory

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def publish(self, present):
        present.is_published = True

    def cancel(self, present):
        present.is_published = False