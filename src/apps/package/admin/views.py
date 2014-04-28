#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, AjaxDetailView, RequestAwareMixin, \
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView, ModelActiveView, AdminRequiredMixin
from apps.package.models import Package
from .forms import PackageForm, PackageDatatablesBuilder

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class PackageListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Package
    datatables_builder_class = PackageDatatablesBuilder
    queryset = Package.active_objects.get_empty_query_set()


class PackageListDatatablesView(AjaxDatatablesView):
    model = Package
    datatables_builder_class = PackageListView.datatables_builder_class
    queryset = Package.active_objects.order_by('-updated')


class PackageCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = Package
    form_class = PackageForm
    template_name = 'package/admin/package.form.inc.html'


class PackageEditView(ModelAwareMixin, AjaxUpdateView):
    model = Package
    form_class = PackageForm
    form_action_url_name = 'admin:package:package_edit'
    template_name = 'package/admin/package.form.inc.html'


class PackageDeleteView(ModelActiveView):
    model = Package


class PackageUpdateView(AjaxSimpleUpdateView):
    model = Package

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def publish(self, package):
        package.is_published = True

    def cancel(self, package):
        package.is_published = False