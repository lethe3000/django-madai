#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import password_reset
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.http import base36_to_int

from django.views.generic import DetailView, UpdateView, View
from django.template import RequestContext
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, render_to_response
from django.views.generic.base import TemplateResponseMixin
from apps.common import exceptions
from apps.common.admin.views import HttpResponseJson
from apps.common.website.views import LoginRequiredMixin

from apps.customer.models import Customer
from apps.customer.website.forms import ProfileBaseForm, ProfileChangePasswordForm, ProfileResetPasswordForm, LoginForm, CustomerRegisterForm


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ProfileResetPassword(TemplateResponseMixin, View):
    template_name = 'customer/website/customer.reset.password.html'
    form_class = ProfileResetPasswordForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return self.render_to_response(context=context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return password_reset(request=self.request, **self.kwargs)
        else:
            context = {'form': form}
            return self.render_to_response(context=context)


class ProfilePostResetPassword(TemplateResponseMixin, View):
    template_name = 'customer/website/customer.post.reset.password.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(context=None)


class SigninView(View):

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.auth_user)
            response_data = exceptions.build_success_response_result()
            return HttpResponseJson(response_data, self.request);
        else:
            raise exceptions.AjaxValidateFormFailed(errors=form.errors)


class SignupView(View):

    def post(self, request, *args, **kwargs):
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            form.save(request)
            auth.login(request, form.auth_user)
            response_data = exceptions.build_success_response_result()
            return HttpResponseJson(response_data, self.request);
        else:
            raise exceptions.AjaxValidateFormFailed(errors=form.errors)


class ToEmailConfirmView(TemplateResponseMixin, View):
    template_name = 'customer/website/to_email_confirm.html'

    def dispatch(self, request, *args, **kwargs):
        return self.render_to_response(locals())


# request,
# uidb36=None,
# token=None,
# token_generator=default_token_generator
class EmailConfirmView(TemplateResponseMixin, View):
    template_name = 'customer/website/email_confirm_complete.html'
    token_generator = default_token_generator
    UserModel = get_user_model()

    def get(self, request, *args, **kwargs):
        uidb36 = kwargs['uidb36']
        token = kwargs['token']
        assert uidb36 is not None and token is not None
        try:
            uid_int = base36_to_int(uidb36)
            user = self.UserModel._default_manager.get(pk=uid_int)
        except (ValueError, OverflowError, self.UserModel.DoesNotExist):
            user = None
        if user and self.token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            valid_link = True
        else:
            valid_link = False
        context = {
            'valid_link': valid_link
        }
        return self.render_to_response(context=context)


class LogoutView(View):
    def dispatch(self, request, *args, **kwargs):
        auth.logout(request)
        return HttpResponseRedirect(reverse('website:index'))