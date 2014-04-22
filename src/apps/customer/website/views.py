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


class ProfileSidebarMixin(object):
    def get_context_data(self, **kwargs):
        context = super(ProfileSidebarMixin, self).get_context_data(**kwargs)
        context['sidebar_tag'] = self.sidebar_tag
        return context


class ProfileBasicView(LoginRequiredMixin, ProfileSidebarMixin, UpdateView):
    form_class = ProfileBaseForm
    template_name = 'customer/website/customer.profile.html'
    model = Customer
    sidebar_tag = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.customer

    # No need to obey default behavior that redirects to success url.
    # Returning the saved form and giving 'saved=true' hint is what we expect of. So override form_valida()
    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_response(self.get_context_data(form=form, saved="true"))


class CustomerCenterView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customer/website/home.html'
    context_object_name = 'customer'

    def get_object(self, queryset=None):
        return Customer.objects.filter(pk=self.request.user.id)


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


class ProfileChangePassword(LoginRequiredMixin, ProfileSidebarMixin, UpdateView):
    form_class = ProfileChangePasswordForm
    template_name = 'customer/website/customer.change.password.html'
    model = Customer
    sidebar_tag = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.customer

    # No need to obey default behavior that redirects to success url.
    # Returning the saved form and giving 'saved=true' hint is what we expect of. So override form_valida()
    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_response(self.get_context_data(form=form, saved="true"))


class CustomerFeedbackView(LoginRequiredMixin, ProfileSidebarMixin, DetailView):
    template_name = 'customer/website/customer.feedback.html'
    sidebar_tag = 'feedback'

    def get_object(self, queryset=None):
        return self.request.user.customer

    def post(self, request, *args, **kwargs):
        self.send_message()
        return redirect('website:customer:customer_feedback')

    def send_message(self):
        name = self.request.user.customer
        phone = self.request.user.phone
        message = self.request.POST.get('remarks', None)
        if not message:
            return

        mail_subject = u'应用工厂客户联系 %s ' % self.request.user.customer.email
        mail_content = u'有客户提交了联系方式:\n姓名：%s \n 联系方式: %s \n 留言:%s 请速联系!' % (name, phone, message)
        try:
            send_mail(mail_subject,
                      mail_content,
                      settings.EMAIL_HOST_USER,
                      [settings.FAC_OFFICIAL_EMAIL],
                      fail_silently=False)
        except Exception as e:
            logger.error("failed to send email error = %s %s" % (e.message, e.__class__.__name__))


class HomeView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return render_to_response('customer/website/home.html',
                                  locals(),
                                  context_instance=RequestContext(request))


class LoginView(View):

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.auth_user)
            response_data = exceptions.build_success_response_result()
            return HttpResponseJson(response_data, self.request);
        else:
            raise exceptions.AjaxValidateFormFailed(errors=form.errors)


class SignUpView(View):

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