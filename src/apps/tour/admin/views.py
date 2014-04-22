#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, ListView
import os
from apps.tour.models import Article
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, AjaxDetailView, RequestAwareMixin,\
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView, ModelActiveView, AdminRequiredMixin
from apps.tour.models import Scenery, GuideType
from .forms import ArticleForm, ArticleDatatablesBuilder, SceneryDatatablesBuilder, SceneryForm, GuideTypeForm, GuideTypeDatatablesBuilder
from utils.db.queryutil import get_object_or_none

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ArticleListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Article
    datatables_builder_class = ArticleDatatablesBuilder
    queryset = Article.objects.get_empty_query_set()


class ArticleListDatatablesView(AjaxDatatablesView):
    model = Article
    datatables_builder_class = ArticleListView.datatables_builder_class
    queryset = Article.active_objects.select_related("scenery", "guide_type", "creator").order_by('-updated')


class ArticleCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = Article
    form_class = ArticleForm
    form_action_url_name = 'admin:tour:article_create'
    template_name = 'tour/admin/article.form.inc.html'

    def get_initial(self):
        initial = super(ArticleCreateView, self).get_initial()
        try:
            initial["scenery"] = self.request.GET['scenery']
            initial["guide_type"] = self.request.GET['guidetype']
        except KeyError:
            pass
        return initial


class ArticleEditView(ModelAwareMixin, AjaxUpdateView):
    model = Article
    form_class = ArticleForm
    form_action_url_name = 'admin:tour:article_edit'
    template_name = 'tour/admin/article.form.inc.html'

    def get_initial(self):
        initial = super(ArticleEditView, self).get_initial()
        if self.object:
            initial["content_html"] = self.object.content_html()
        return initial


class ArticleDeleteView(ModelActiveView):
    model = Article


class ArticlePreviewView(ModelAwareMixin, AjaxDetailView):
    model = Article
    template_name = 'tour/admin/article.preview.inc.html'


class ArticleHtmlRedirectView(RedirectView):
    def get_redirect_url(self, pk):
        article = get_object_or_404(Article, pk=pk)
        return article.content_file.url


class ArticleUpdateView(AjaxSimpleUpdateView):
    model = Article

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
