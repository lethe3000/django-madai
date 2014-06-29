#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from django.contrib.auth.models import  UserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.db import models

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class StaffManager(models.Manager):
    def get_query_set(self):
        return super(StaffManager, self).get_query_set().filter(is_staff=True)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(verbose_name='名称',
                            max_length=30,
                            unique=True)

    email = models.EmailField(verbose_name='账号(邮箱地址)',
                              blank=True,
                              default="")

    nick_name = models.CharField(verbose_name='昵称',
                                 max_length=30,
                                 blank=True,
                                 default="")

    phone = models.CharField(max_length=32,
                             default='',
                             blank=True,
                             verbose_name=u'电话')

    qq = models.CharField(max_length=32,
                          default='',
                          blank=True,
                          verbose_name=u'qq')

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = (
        (GENDER_MALE, u'男'),
        (GENDER_FEMALE, u'女'),
    )

    gender = models.CharField(max_length=12, choices=GENDER_CHOICES,
                              default=GENDER_MALE,
                              blank=True,
                              verbose_name=u'性别')

    is_staff = models.BooleanField(_('staff status'),
                                   default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'),
                                    default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()
    staffs = StaffManager()

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%d/" % self.id

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        "Returns the short name for the user."
        return self.name

    def is_admin(self):
        return self.is_superuser

    def is_customer(self):
        return not self.is_staff

    def __unicode__(self):
        return self.get_full_name()
