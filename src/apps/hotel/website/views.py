#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.generic.base import TemplateResponseMixin, View, RedirectView
from django.views.generic.list import BaseListView
from apps.tour.models import Article, Scenery, GuideType


class ArticleListView(TemplateResponseMixin, BaseListView):
    paginate_by = 10
    model = Article
    template_name = 'tour/website/article.list.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        scenery_id = self.kwargs['scenery'];
        return Article.active_objects.filter(scenery=scenery_id).all()


class SceneryListView(TemplateResponseMixin, View):
    template_name = 'tour/website/scenery.list.html'

    def get(self, request, *args, **kwargs):
        scenery_list = Scenery.active_objects.all()
        return self.render_to_response(locals())


class SceneryView(TemplateResponseMixin, View):
    template_name = 'tour/website/scenery.html'

    def get(self, request, *args, **kwargs):
        scenery = Scenery.active_objects.get(pk=self.kwargs['pk'])
        guide_type_list = GuideType.active_objects.filter(articles__scenery=scenery)\
                                                  .only('name', 'image_file', 'summary')\
                                                  .distinct()
        return self.render_to_response(locals())


class LatestArticleContentView(RedirectView):

    def get_redirect_url(self, **kwargs):
        scenery_id = self.kwargs['scenery']
        guide_type_id = self.kwargs['guide_type']
        article = Article.objects.latest_article(scenery_id, guide_type_id)
        return article.content_url()