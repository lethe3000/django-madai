#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from captcha.fields import CaptchaField

from django import forms
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.utils.http import int_to_base36
from apps.api.serializers import Hao3sMixin
from rest_framework.authtoken.models import Token

from apps.customer.models import Customer


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ProfileBaseForm(forms.ModelForm):
    phone = forms.RegexField(regex='^1\d{10}$',
                             error_message=u'手机号码不正确',
                             widget=forms.TextInput(attrs={"required": "true"}))

    def __init__(self, *args, **kwargs):
        super(ProfileBaseForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs['class'] = "form-control"
        self.fields['address'].widget.attrs['class'] = "form-control"

    class Meta:
        model = Customer
        fields = ('phone', 'address')


class ProfileChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField(label=u'当前登录密码',
        widget=forms.PasswordInput(attrs={"required": "true"}),
        help_text=u'必填.')

    password1 = forms.CharField(label=u'新密码',
        widget=forms.PasswordInput(attrs={"required": "true"}),
        help_text=u'必填.')

    password2 = forms.CharField(label=u'确认新密码',
        widget=forms.PasswordInput(attrs={"required": "true"}),
        help_text=u'必填. 请再次输入密码以确认.')

    def __init__(self, *args, **kwargs):
        super(ProfileChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = "form-control"
        self.fields['password1'].widget.attrs['class'] = "form-control"
        self.fields['password2'].widget.attrs['class'] = "form-control"

    def clean_old_password(self):
        password = self.cleaned_data.get('old_password')
        user = auth.authenticate(email=self.instance.email, password=password)
        if not user:
            raise forms.ValidationError(u'当前登录密码不正确')
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次输入的密码不匹配')
        return password2

    def save(self, commit=False):
        user = self.instance
        new_password = self.cleaned_data['password2']
        user.set_password(new_password)
        user.save()
        return user


class ProfileResetPasswordForm(forms.Form):
    email = forms.EmailField(label=u'电子邮件', error_messages={
        'invalid': '输入一个有效的 Email 地址。',
    })

    def __init__(self, *args, **kwargs):
        super(ProfileResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = "required form-control"

    def clean_email(self):
        UserModel = get_user_model()
        email = self.cleaned_data['email']
        users_cache = UserModel._default_manager.filter(email__iexact=email)
        if not users_cache:
            raise forms.ValidationError(u'邮箱地址无效')
        return email

class LoginForm(forms.Form):
    name = forms.CharField(label=u'账号',
                           max_length=75, # the same as User.email
                           widget=forms.TextInput(attrs={'placeholder': u'邮箱',
                                                         'class': 'form-control'}))

    password = forms.CharField(label=u'密码',
                               widget=forms.PasswordInput(attrs={'placeholder': u'登录密码',
                                                                 'class': 'form-control'}))

    keep_login = forms.BooleanField(label=u'保持15天在线', required=False)

    def clean_password(self):
        name = self.cleaned_data.get('name')
        password = self.cleaned_data.get('password')
        user = auth.authenticate(name=name, password=password)
        if not user:
            raise forms.ValidationError(u'账号或密码错误')
        else:
            self.auth_user = user
        return password


class CustomerRegisterForm(Hao3sMixin, forms.Form):

    name = forms.RegexField(label=u'用户名',
                            max_length=30,
                            help_text=u'必填.',
                            regex="^[\w.@+-]+$",
                            error_message=u"只能包含数字、字母、'.'、'+'、'-'、'@'")

    password1 = forms.CharField(label=u'创建密码',
                                widget=forms.PasswordInput,
                                help_text=u'必填.')
    password2 = forms.CharField(label=u'再次确认密码',
                                widget=forms.PasswordInput,
                                help_text=u'必填. 请再次输入密码以确认.')

    captcha = CaptchaField(label=u'输入图片中的文字', error_messages=dict(invalid=u'验证码错误'))

    def __init__(self, *args, **kwargs):
        super(CustomerRegisterForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required form-control"
        self.fields['password1'].widget.attrs['class'] = "required form-control"
        self.fields['password2'].widget.attrs['class'] = "required form-control"
        self.fields['captcha'].widget.attrs['class'] = "required form-control"

    def clean_name(self):
        UserModel = get_user_model()
        name = self.cleaned_data['name']
        users_cache = UserModel._default_manager.filter(name__iexact=name)
        if users_cache:
            raise forms.ValidationError(u'用户名已被注册')
        if self.has_username_in_hao3s(name):
            raise forms.ValidationError(u'用户名已经被使用')
        return name

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次输入的密码不匹配')
        return password2

    def send_email(self, request, user,
                   subject_template_name='customer/website/sign_up_subject.txt',
                   email_template_name='customer/website/sign_up_email.html',
                   token_generator=default_token_generator):
        from django.core.mail import send_mail
        site_name = settings.SITE_NAME
        domain = site_name
        c = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': int_to_base36(user.pk),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': request.is_secure() and 'https' or 'http',
        }
        subject = loader.render_to_string(subject_template_name, c)
        email = loader.render_to_string(email_template_name, c)
        # Email subject不换行
        subject = settings.EMAIL_SUBJECT_PREFIX + ' ' + ''.join(subject.splitlines())
        send_mail(subject, email, None, [user.email])

    def save(self, request):
        name = self.cleaned_data['name']
        password = self.cleaned_data['password1']
        sync_success = self.sync_account_to_hao3s(name, password)
        new_user = Customer(is_active=True,
                            is_staff=False,
                            name=name,
                            has_sync_to_thirdparty=sync_success)
        new_user.set_password(password)
        new_user.save()
        self.auth_user = auth.authenticate(name=self.cleaned_data['name'],
                                           password=self.cleaned_data['password1'])
        Token.objects.get_or_create(user=new_user)
        # We don't need to send verification email now.
        # self.send_email(request=request, user=new_user)
        return new_user