#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
import logging
import subprocess
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponse

from os import environ
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
import os
from apps.tour.models import Scenery
from apps.hotel.models import Hotel
from apps.flight.models import Flight

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


def build_menu(request):
    SUBMENU_ACCOUNT = [
        ('用户组', reverse('admin:account:group_list'), lambda request: request.user.is_admin()),
        ('账号管理', reverse('admin:account:user_list'), lambda request: request.user.is_admin()),
        ('修改密码', reverse('admin:account:change_password', kwargs={'pk': request.user.id}),None),
    ]

    SUBMENU_CUSTOMER = [
        ('客户', reverse('admin:customer:customer_list'), lambda request: request.user.is_admin() or
                                                                          request.user.has_perm('view_customer')),
    ]

    SUBMENU_HOTEL = [
        ('酒店', reverse('admin:hotel:hotel_list'), None),
        ('酒店资讯类型', reverse('admin:hotel:infotype_list'), None),
        ('酒店资讯', reverse('admin:hotel:hotelarticle_list'), None),
    ]

    SUBMENU_FLIGHT = [
        ('航班', reverse('admin:flight:flight_list'), None),
        ('航班资讯类型', reverse('admin:flight:infotype_list'), None),
        ('航班资讯', reverse('admin:flight:flightarticle_list'), None),
    ]

    SUBMENU_PACKAGE = [
        ('套餐', reverse('admin:package:package_list'), None),
    ]

    SUBMENU_ORDER = [
        ('订单', reverse('admin:order:order_list'), None),
    ]

    MENU = (
        {'menu': '系统信息', 'url': reverse('admin:dashboard'), 'icon': 'icon-dashboard', 'submenu': []},
        {'menu': '账号', 'url': '', 'icon': 'icon-group', 'submenu': SUBMENU_ACCOUNT},
        {'menu': '客户', 'url': '', 'icon': 'icon-user', 'submenu': SUBMENU_CUSTOMER},
        {'menu': '酒店', 'url': '', 'icon': 'icon-bookmark', 'submenu': SUBMENU_HOTEL},
        {'menu': '酒店dashboard', 'url': '', 'icon': 'icon-bookmark', 'submenu': build_hotel_submenu()},
        {'menu': '航班', 'url': '', 'icon': 'icon-bookmark', 'submenu': SUBMENU_FLIGHT},
        {'menu': '航班dashboard', 'url': '', 'icon': 'icon-bookmark', 'submenu': build_flight_submenu()},
        {'menu': '套餐', 'url': '', 'icon': 'icon-bookmark', 'submenu': SUBMENU_PACKAGE},
        {'menu': '订单', 'url': '', 'icon': 'icon-bookmark', 'submenu': SUBMENU_ORDER},
    )
    menus = []
    for item in MENU:
        has_permission = False
        menu = {"name": item['menu'], "url": item['url'], "icon": item['icon'], "submenus": []}
        for subitem in item['submenu']:
            if subitem[2] is None or (subitem[2] and subitem[2](request)):
                has_permission = True
                menu['submenus'].append({"name": subitem[0], "url": subitem[1]})
        if has_permission or menu['url']:
            menus.append(menu)
    # remove menu with empty submenu
    return [menu for menu in menus if menu['url'] or menu['submenus']]


def build_sencery_submenu():
    return [(scenery.name, reverse('admin:tour:scenery_dashboard', kwargs={'pk': scenery.id}), None) for scenery in Scenery.active_objects.all()]


def build_hotel_submenu():
    return [(hotel.name, reverse('admin:hotel:hotel_dashboard', kwargs={'pk': hotel.id}), None) for hotel in Hotel.active_objects.all()]


def build_flight_submenu():
    return [(flight.name, reverse('admin:flight:flight_dashboard', kwargs={'pk': flight.id}), None) for flight in Flight.active_objects.all()]


def home(request):
    """
    重定向到login页面
    """
    site_name = settings.SITE_NAME
    if request.user.is_authenticated():
        if not request.user.is_staff:
            return redirect(reverse('website:customer:customer_home'))
        menus = build_menu(request)
        return render_to_response('admin/home.html',
                                  locals(),
                                  context_instance=RequestContext(request))

    # 如果没有登陆，返回默认的主页
    return redirect(reverse('admin:account:login'))


@login_required()
def dashboard(request):
    try:
        env_settings = environ['DJANGO_SETTINGS_MODULE']
    except KeyError:
        env_settings = "not define in env"

    # get which tag is using in current branch
    #cmd = 'cd %s && git describe --abbrev=0 --tags' % settings.SITE_ROOT
    cmd = 'cd %s && git rev-list --date-order -n 1 --format=%%d HEAD' % settings.SITE_ROOT
    git_tag = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)

    active_settings = settings.SETTINGS_MODULE

    return render_to_response('admin/dashboard.inc.html',
                              locals(),
                              context_instance=RequestContext(request))


@login_required()
def loaddata(request, filename):
    if not request.user.is_superuser:
        raise PermissionDenied
    call_command("loaddata", filename, settings=settings.SETTINGS_MODULE, traceback=True, verbosity=0)
    return HttpResponse(content='load data %s success' % filename)


@login_required()
def initdata(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    call_command("loaddata", "initial_data.json", settings=settings.SETTINGS_MODULE, traceback=True, verbosity=0)
    return HttpResponse(content='load data initial_data.json success')

