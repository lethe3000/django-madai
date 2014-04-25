#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import logging
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
import os
from django import forms
from apps.tour.models import Article
from apps.common.ace import AceClearableFileInput, AceBooleanField
from apps.common.admin.datatables import DatatablesIdColumn, DatatablesBuilder, DatatablesImageColumn, DatatablesTextColumn,\
    DatatablesBooleanColumn, DatatablesUserChoiceColumn, DatatablesDateTimeColumn, DatatablesColumnActionsRender,\
    DatatablesActionsColumn, DatatablesModelChoiceColumn, DatatablesIntegerColumn
from apps.tour.models import Scenery, GuideType

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ArticleForm(forms.ModelForm):
    content_html = forms.CharField(label=u'内容',
                                   widget=forms.Textarea())

    is_pinned = AceBooleanField(required=False,
                                label=u'Banner显示')

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = "required col-md-10 limited"
        self.fields['summary'].widget.attrs['class'] = "col-md-10"
        self.fields['desc'].widget.attrs['class'] = "col-md-10"
        self.fields['scenery'].widget.attrs['class'] = "col-md-5"
        self.fields['scenery'].queryset = Scenery.active_objects.only("name").all()
        self.fields['guide_type'].widget.attrs['class'] = "col-md-5"
        guidetype_queryset = GuideType.active_objects.only("name")
        if kwargs.get('initial').has_key('guide_type'):
            guidetype = int(kwargs.get('initial').get('guide_type'))
            guidetype_queryset = guidetype_queryset.filter(id=guidetype)
        self.fields['guide_type'].queryset = guidetype_queryset.all()
        self.fields['web_link'].widget.attrs['class'] = "col-md-10"
        self.fields['source'].widget.attrs['class'] = "col-md-10"

    class Meta:
        model = Article
        fields = (
            'title', 'title_image_file', 'scenery', 'guide_type', "summary", 'web_link', 'is_pinned', 'display_order', 'source', 'desc', 'content_html')

        widgets = {
            # use FileInput widget to avoid show clearable link and text
            'title_image_file': AceClearableFileInput(),
        }

    def clean(self):
        cleaned_data = super(ArticleForm, self).clean()
        # keep the old image and delete it if changed at save()
        self.old_title_image_file = self.instance.title_image_file
        return cleaned_data

    # responsive header for mobile display.
    # 1. don't allow scale the content view
    # 2. scale the image according to device width.
    RESPONSIVE_HEADER = """\
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1.0, minimum-scale=1.0{0}"/>
    <style>
    img {{
        display: block;
        height: auto;
        max-width: 100%;
    }}
    </style>
</head>
"""
    HEADER_NO_SCALE_FACTOR = ', maximum-scale=1.0'
    def save(self, commit=False):
        article = super(ArticleForm, self).save(commit)
        #mock a html file to feed to article.content_file
        if article.content_file:
            # update it if has content file
            with open(article.content_file.path, 'w') as f:
                f.write(self.cleaned_data['content_html'].encode('utf-8'))
        else:
            buf = StringIO.StringIO(self.cleaned_data['content_html'].encode('utf-8'))
            self.RESPONSIVE_HEADER = self.RESPONSIVE_HEADER.format(
                self.HEADER_NO_SCALE_FACTOR if self.instance.guide_type_id != GuideType.GUIDE_TYPE_MAP else ''
            )
            article.content_file = SimpleUploadedFile("content.html", self.RESPONSIVE_HEADER + buf.read())

        if not hasattr(article, "creator"):
            article.creator = self.initial['request'].user
        article.save()
        # return id to avoid caller to model.save() again
        return article


class ArticleDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    title = DatatablesTextColumn(label=u'标题',
                                 is_searchable=True,
                                 render=(lambda request, model, field_name:
                                         u"<a href='%s' target='_blank'>%s</a>" % (model.content_url(), model.title)))


    title_image_file = DatatablesImageColumn(label='标题图片')

    summary = DatatablesTextColumn(label=u'摘要',
                                   is_searchable=True)

    scenery = DatatablesModelChoiceColumn(label=u'景区',
                                          is_searchable=True,
                                          queryset=Scenery.active_objects.only('name').all())

    guide_type = DatatablesModelChoiceColumn(label='资料类型',
                                             is_searchable=True,
                                             queryset=GuideType.active_objects.only('name').all())

    is_published = DatatablesBooleanColumn((('', u'全部'), (1, u'发布'), (0, u'草稿')),
                                           label='状态',
                                           is_searchable=True,
                                           col_width='7%',
                                           render=(lambda request, model, field_name:
                                                   u'<span class="label label-info"> 发布 </span>' if model.is_published else
                                                   u'<span class="label label-warning"> 草稿 </span>'))

    web_link = DatatablesTextColumn(label=u'外部链接',
                                    render=(lambda request, model, field_name:
                                             u"<a href='%s' target='_blank'>链接</a>" % model.web_link if model.web_link else ""))

    is_pinned = DatatablesBooleanColumn(label=u'banner显示',
                                        col_width='5%')

    creator = DatatablesUserChoiceColumn(label='作者',)

    updated = DatatablesDateTimeColumn(label='修改时间')

    def actions_render(request, model, field_name):
        action_url_builder = lambda model, action: reverse('admin:tour:article_update', kwargs={'pk': model.id, 'action_method': action})
        if model.is_published:
            actions = [{'is_link': False, 'css_class': 'btn-yellow', 'name': 'cancel', 'url': action_url_builder(model, 'cancel'),
                        'text': u'撤销', 'icon': 'icon-cut'}]
        else:
            actions = [{'is_link': True, 'css_class': 'btn-info', 'name': 'edit', 'text': u'编辑', 'icon': 'icon-edit'},
                       {'is_link': False, 'css_class': 'btn-warning', 'name': 'publish',
                        'url': action_url_builder(model, 'publish'), 'text': u'发布', 'icon': 'icon-save'}]
        #actions.append({'is_link': True, 'css_class': 'btn-pink', 'name': 'preview', 'text': u'预览', 'icon': 'icon-camera'})
        actions.append({'is_link': False, 'css_class': 'btn-warning', 'name': 'delete', 'text': u'删除', 'icon': 'icon-remove'})
        return DatatablesColumnActionsRender(actions=actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)


class SceneryForm(forms.ModelForm):

    is_virtual = AceBooleanField(label=u'虚拟景区', required=False)

    def __init__(self, *args, **kwargs):
        super(SceneryForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required col-md-10 limited"
        self.fields['summary'].widget.attrs['class'] = "col-md-10 limited"

    class Meta:
        model = Scenery
        fields = ('name', 'image_file', 'summary', 'display_order', 'is_virtual', 'thirdparty_id', 'phone_contact', 'phone_sos')

        widgets = {
            # use FileInput widget to avoid show clearable link and text
            'image_file': AceClearableFileInput(),
        }


class SceneryDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label=u'名称',
                                is_searchable=True)

    image_file = DatatablesImageColumn(label=u'图片')

    summary = DatatablesTextColumn(label=u'简介',)

    is_virtual = DatatablesBooleanColumn(label=u'虚拟景区')

    phone = DatatablesBooleanColumn(label=u'电话',
                                    render=(lambda request, model, field_name:
                                            u'<ul><li>%s</li><li>%s</li></ul>' % (model.phone_contact, model.phone_sos)))

    display_order = DatatablesIntegerColumn(label=u'显示顺序',
                                            is_searchable=True,
                                            col_width="4%")

    is_active = DatatablesBooleanColumn((('', u'全部'), (1, u'激活'), (0, u'锁定')),
                                        label='状态',
                                        is_searchable=True,
                                        col_width='5%',
                                        render=(lambda request, model, field_name:
                                                u'<span class="label label-info"> 启用 </span>' if model.is_active else
                                                u'<span class="label label-warning"> 禁用 </span>'))

    def actions_render(request, model, field_name):
        action_url_builder = lambda model, action: reverse('admin:tour:scenery_update', kwargs={'pk': model.id, 'action_method': action})

        if model.is_active:
            actions = [{'is_link': False, 'name': 'lock', 'text': u'锁定',
                        'icon': 'icon-lock', "url": action_url_builder(model, "lock")}]
        else:
            actions = [{'is_link': False, 'name': 'unlock', 'text': u'解锁',
                        'icon': 'icon-unlock', "url": action_url_builder(model, "unlock")}]
        actions.append({'is_link': True, 'name': 'edit', 'text': u'编辑',
                        'icon': 'icon-edit', 'url_name': 'admin:tour:scenery_edit'})
        return DatatablesColumnActionsRender(actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)


class GuideTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GuideTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required col-md-10 limited"
        self.fields['summary'].widget.attrs['class'] = "col-md-10 limited"

    class Meta:
        model = GuideType
        fields = ('name', 'image_file', 'summary', 'display_order')

        widgets = {
            # use FileInput widget to avoid show clearable link and text
            'image_file': AceClearableFileInput(),
        }


class GuideTypeDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label=u'名称',
                                is_searchable=True)

    image_file = DatatablesImageColumn(label=u'图片')

    summary = DatatablesTextColumn(label=u'简介',)

    display_order = DatatablesIntegerColumn(label=u'显示顺序',
                                            is_searchable=True)

    is_active = DatatablesBooleanColumn((('', u'全部'), (1, u'激活'), (0, u'锁定')),
                                        label='状态',
                                        is_searchable=True,
                                        col_width='7%',
                                        render=(lambda request, model, field_name:
                                                u'<span class="label label-info"> 启用 </span>' if model.is_active else
                                                u'<span class="label label-warning"> 禁用 </span>'))

    def actions_render(request, model, field_name):
        action_url_builder = lambda model, action: reverse('admin:tour:guidetype_update', kwargs={'pk': model.id, 'action_method': action})
        if model.is_active:
            actions = [{'is_link': False, 'name': 'lock', 'text': u'锁定',
                        'icon': 'icon-lock', "url": action_url_builder(model, "lock")}]
        else:
            actions = [{'is_link': False, 'name': 'unlock', 'text': u'解锁',
                        'icon': 'icon-unlock', "url": action_url_builder(model, "unlock")}]
        actions.append({'is_link': True, 'name': 'edit', 'text': u'编辑',
                        'icon': 'icon-edit', 'url_name': 'admin:tour:guidetype_edit'})
        return DatatablesColumnActionsRender(actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)
