#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import logging
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
import os
from django import forms
from apps.share.models import TravelNote
from apps.common.ace import AceClearableFileInput, AceBooleanField
from apps.common.admin.datatables import DatatablesIdColumn, DatatablesBuilder, DatatablesImageColumn, DatatablesTextColumn, \
    DatatablesBooleanColumn, DatatablesUserChoiceColumn, DatatablesDateTimeColumn, DatatablesColumnActionsRender, \
    DatatablesActionsColumn, DatatablesModelChoiceColumn, DatatablesIntegerColumn


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class TravelNoteForm(forms.ModelForm):
    content_html = forms.CharField(label=u'内容',
                                   widget=forms.Textarea())

    is_pinned = AceBooleanField(required=False,
                                label=u'Banner显示')

    def __init__(self, *args, **kwargs):
        super(TravelNoteForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = "required col-md-10 limited"
        # self.fields['summary'].widget.attrs['class'] = "col-md-10"
        # self.fields['desc'].widget.attrs['class'] = "col-md-10"
        # self.fields['hotel'].widget.attrs['class'] = "col-md-5"
        # self.fields['hotel'].queryset = Hotel.active_objects.only("name").all()
        # self.fields['info_type'].widget.attrs['class'] = "col-md-5"
        # infotype_queryset = InfoType.active_objects.only("name")
        # if kwargs.get('initial').has_key('info_type'):
        #     infotype = int(kwargs.get('initial').get('info_type'))
        #     infotype_queryset = infotype_queryset.filter(id=infotype)
        # self.fields['info_type'].queryset = infotype_queryset.all()
        # self.fields['web_link'].widget.attrs['class'] = "col-md-10"
        # self.fields['source'].widget.attrs['class'] = "col-md-10"

    class Meta:
        model = TravelNote
        fields = (
            'title', 'fake_user', 'fake_head_image', 'is_pinned', 'display_order', 'content_html')

        widgets = {
            # use FileInput widget to avoid show clearable link and text
        }

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
        note = super(TravelNoteForm, self).save(commit)
        #mock a html file to feed to article.content_file
        if note.content_file:
            # update it if has content file
            with open(note.content_file.path, 'w') as f:
                f.write(self.cleaned_data['content_html'].encode('utf-8'))
        else:
            buf = StringIO.StringIO(self.cleaned_data['content_html'].encode('utf-8'))
            self.RESPONSIVE_HEADER = self.RESPONSIVE_HEADER.format(
                # self.HEADER_NO_SCALE_FACTOR if self.instance.info_type_id != InfoType.INFO_TYPE_MAP else ''
                ''
            )
            note.content_file = SimpleUploadedFile("content.html", self.RESPONSIVE_HEADER + buf.read())

        if not hasattr(note, "creator"):
            note.creator = self.initial['request'].user
        note.save()
        # return id to avoid caller to model.save() again
        return note


class TravelNoteDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    title = DatatablesTextColumn(label=u'标题',
                                 is_searchable=True,
                                 render=(lambda request, model, field_name:
                                         u"<a href='%s' target='_blank'>%s</a>" % (model.content_url(), model.title)))

    is_published = DatatablesBooleanColumn((('', u'全部'), (1, u'发布'), (0, u'草稿')),
                                           label='状态',
                                           is_searchable=True,
                                           col_width='7%',
                                           render=(lambda request, model, field_name:
                                                   u'<span class="label label-info"> 发布 </span>' if model.is_published else
                                                   u'<span class="label label-warning"> 草稿 </span>'))

    is_pinned = DatatablesBooleanColumn(label=u'banner显示',
                                        col_width='5%')

    creator = DatatablesUserChoiceColumn(label=u'后台真实作者',)

    fake_user = DatatablesTextColumn(label=u'fake作者',
                                     is_searchable=True)

    fake_head_image = DatatablesImageColumn(label=u'fake作者头像')

    updated = DatatablesDateTimeColumn(label=u'修改时间')

    def actions_render(request, model, field_name):
        action_url_builder = lambda model, action: reverse('admin:share:travelnote_update', kwargs={'pk': model.id, 'action_method': action})
        if model.is_published:
            actions = [{'is_link': False, 'css_class': 'btn-yellow', 'name': 'cancel', 'url': action_url_builder(model, 'cancel'),
                        'text': u'撤销', 'icon': 'icon-cut'}]
        else:
            actions = [{'is_link': True, 'css_class': 'btn-info', 'name': 'edit', 'text': u'编辑', 'icon': 'icon-edit'},
                       {'is_link': False, 'css_class': 'btn-warning', 'name': 'publish',
                        'url': action_url_builder(model, 'publish'), 'text': u'发布', 'icon': 'icon-save'}]
        return DatatablesColumnActionsRender(actions=actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)