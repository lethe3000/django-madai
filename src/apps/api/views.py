#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import get_cache
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
import os
from rest_framework import views, exceptions, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
import time
from apps.api.serializers import ScenerySerializer, GuideTypeSerializer, RegisterSerializer, ResetPasswordSerializer, \
    AlbumCreateSerializer, ArticleSerializer, CustomAvatarSerializer, CustomProfileDetailSerializer, CustomProfileUpdateSerializer, \
    CheckinSerializer, AlbumImageSerializer, AlbumImageCreateSerializer, AlbumSerializer, JournalSerializer,\
    JournalCreateSerializer, AuthTokenSerializer, ChatroomJoinSerializer, ChatroomSerializer, ChatroomCreateSerializer, \
    ChatroomMessageListSerializer, ChatroomMessageSerializer
from apps.chatroom.models import Chatroom
from apps.customer.models import Journal, Customer
from apps.imagestore.models import AlbumImage, Album
from apps.tour.models import Scenery, GuideType, Article

logger = logging.getLogger('apps.'+os.path.basename(os.path.dirname(__file__)))


def build_etag_objects_response(etag, objects, resp_status=status.HTTP_200_OK):
    return Response(data={'etag': etag, 'objects': objects}, status=resp_status)

def build_simple_json_response(data):
    content_type = 'application/json; charset=utf-8'
    return HttpResponse(content=data, content_type=content_type)

INVALID_TAG = '0'
CACHE_TIMEOUT_SEC = 5 * 60 # 5 minutes

def get_etag_from_model(model_class):
    try:
        # XXX: intend not to use active_objects. we should consider the deactive object as etag value.
        latest_obj = model_class.objects.only('updated').latest()
        return str(latest_obj.updated_timestamp())
    except model_class.DoesNotExist:
        return INVALID_TAG


class LoginView(CreateAPIView):
    """
    登陆.
    登陆成功后服务器返回token, 客户端在调用授权API时,需要把该token放在http header. 具体如下:
        'Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'<br>
    <b>注意: 1. 只有特殊声明需要授权调用的API才需要token.
            2. 客户端通过token访问敏感资源. 如果服务器应答401, 说明token已经无效, 客户端需要显示登录界面引导用户重新登录
    </b>
    """
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.DATA)
        if serializer.is_valid():
            return Response(data={'token': serializer.object['user'].auth_token.key})
        raise exceptions.ParseError(serializer.errors)


class RegisterView(CreateAPIView):
    """
    注册用户.
    注册成功后服务器返回token, 客户端在调用授权API时,需要把该token放在http header. 具体参考LoginView
    """
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA, partial=True)
        if serializer.is_valid():
            return Response(data={'token': serializer.object['token']})
        raise exceptions.ParseError(serializer.errors)


# FIXME 由于password_reset被csrf_protected限制，这里复制一个忽略csrf的password_reset版本
def password_reset_exempt(request, is_admin_site=False,
                          template_name='registration/password_reset_form.html',
                          email_template_name='registration/password_reset_email.html',
                          subject_template_name='registration/password_reset_subject.txt',
                          password_reset_form=PasswordResetForm,
                          token_generator=default_token_generator,
                          post_reset_redirect=None,
                          from_email=None,
                          current_app=None,
                          extra_context=None):
    """
    copy of django.contrib.auth.views.password_reset
    """
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_done')
    if request.method == "POST":
        form = password_reset_form(request.DATA)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
        }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


class ResetPasswordView(CreateAPIView):
    """
    重置密码.
    如果成功返回200, 否则400
    """
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA, partial=True)
        if serializer.is_valid():
            # XXX: keep consistent with url "customer_reset_password"
            kwargs = {'post_reset_redirect': reverse('website:customer:post_reset_password'),
                      'template_name': 'customer/website/customer.reset.password.html',
                      'email_template_name': 'customer/website/customer.reset.password.email.html',
                      'subject_template_name': 'customer/website/customer.reset.password.subject.txt'}
            res = password_reset_exempt(request=self.request, **kwargs)
            if res.status_code in (status.HTTP_200_OK, status.HTTP_302_FOUND):
                return Response(status=status.HTTP_200_OK)
            else:
                raise exceptions.ParseError({})
        raise exceptions.ParseError(serializer.errors)


class CustomerDetailMixin(object):
    def detail_response(self):
        detail = CustomProfileDetailSerializer(instance=self.request.user.customer)
        return build_etag_objects_response(str(self.request.user.customer.updated_timestamp()), [detail.data])


class CustomerAvatarView(CustomerDetailMixin, CreateAPIView):
    """
    更新头像.
    头像图片通过form表单上传. 如果成功,返回完整的用户信息.
    注意: 客户端需要限制头像的大小.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token. 参考LoginView
    """
    serializer_class = CustomAvatarSerializer
    permission_classes = (IsAuthenticated,)

    # test command like below with httppie
    #   >> http -f POST 127.0.0.1:8020/api/customer/avatar/update/ "Authorization: Token 1" avatar@~/Downloads/1393169779_91.png
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA, files=request.FILES, instance=self.request.user.customer)
        if serializer.is_valid():
            serializer.save()
            return self.detail_response()
        raise exceptions.ParseError(serializer.errors)


class CustomerProfileDetailView(CustomerDetailMixin, RetrieveAPIView):
    """
    获取用户profile.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token. 参考LoginView
    其中: gender 取值范围是 'M': 男, 'F':女
    """
    serializer_class = CustomProfileDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.customer

    def get(self, request, *args, **kwargs):
        return self.detail_response()


class CustomerProfileUpdateView(CustomerDetailMixin, GenericAPIView):
    """
    更新用户profile.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token. 参考LoginView
    其中: gender 取值范围是 'M': 男, 'F':女
    如果成功,返回完整的用户信息.
    """
    serializer_class = CustomProfileUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA, instance=self.request.user.customer)
        if serializer.is_valid():
            serializer.save()
            return self.detail_response()
        raise exceptions.ParseError(serializer.errors)


class CheckinView(GenericAPIView):
    """
    check in
    checkin到服务器, 返回当前最新的app信息和模块的etag信息. 客户端通过检查返回模块的etag值, 来决定是否同步模块数据.
    os -- 可选. 取值范围是 "Android" 或 "iOS". 如果不填,默认是Android
    """
    serializer_class = CheckinSerializer

    def get(self, request, *args, **kwargs):
        serializer = CheckinSerializer(context={"os": self.request.GET.get('os'), "user": self.request.user})
        return Response(serializer.data)


class EtagCheckMixin(object):
    """
    A mixin to make "request" object available to Form.
    """
    def check_etag(self, request):
        client_etag = request.QUERY_PARAMS.get('etag', "")
        server_etag = get_etag_from_model(self.model)
        if client_etag == server_etag:
            return None

        return server_etag


class SceneryListView(EtagCheckMixin, ListAPIView):
    """
    获取景区列表.
     etag -- 可选. 景区列表的etag, 通过上次接口返回. 通过url的parameter传递. 如果服务器通过etag检查没有变化, 返回304.<br> 如果不传递etag, 服务器返回所有数据
    """
    serializer_class = ScenerySerializer
    model = Scenery

    def get(self, request, *args, **kwargs):
        etag = self.check_etag(request)
        if not etag:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        serializer = self.serializer_class(Scenery.active_objects.all(), many=True)
        return build_etag_objects_response(etag, serializer.data)


class GuideTypeListView(EtagCheckMixin, ListAPIView):
    """
    获取guide类别列表.
     etag -- 可选. 类别列表的etag, 通过上次接口返回. 通过url的parameter传递.如果服务器通过etag检查没有变化, 返回304.<br> 如果不传递etag, 服务器返回所有数据
    """
    serializer_class = GuideTypeSerializer
    model = GuideType

    def get(self, request, *args, **kwargs):
        etag = self.check_etag(request)
        if not etag:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        serializer = self.serializer_class(GuideType.active_objects.all(), many=True)
        return build_etag_objects_response(etag, serializer.data)


class ArticleListView(EtagCheckMixin, ListAPIView):
    """
    获取文章列表.
     etag -- 可选. 类别列表的etag, 通过上次接口返回. 通过url的parameter传递. 如果服务器通过etag检查没有变化, 返回304.<br> 如果不传递etag, 服务器返回所有数据
    """
    serializer_class = ArticleSerializer
    model = Article

    def get(self, request, *args, **kwargs):
        etag = self.check_etag(request)
        if not etag:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        serializer = self.serializer_class(Article.objects.published_objects(), many=True)
        return build_etag_objects_response(etag, serializer.data)


class AlbumListView(EtagCheckMixin, ListAPIView):
    """
    获取用户相册列表.
    <font color=red>该API需要授权访问</font>. 调用者需要在http header中传递token. 参考LoginView

     etag -- 可选. 类别列表的etag, 通过上次接口返回. 通过url的parameter传递. 如果服务器通过etag检查没有变化, 返回304.<br> 如果不传递etag, 服务器返回所有数据
    """
    permission_classes = (IsAuthenticated,)
    model = Album
    serializer_class = AlbumSerializer

    def get(self, request, *args, **kwargs):
        etag = self.check_etag(request)
        if not etag:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        albums = Album.active_objects.filter(user=request.user)
        serializer = self.serializer_class(albums, many=True)
        return build_etag_objects_response(etag, serializer.data)


class EtagModelMixin(object):
    """
    A mixin to check etag to determinate return a current model or whole models.
    """
    def detail_or_list_response(self, etag, serializer_class, model, **model_filters):
        is_consistent = not etag or etag == INVALID_TAG
        # check whether client and server data consistent with etag.
        if is_consistent:
            detail_serializer = serializer_class(instance=model)
            return build_etag_objects_response(str(model.updated_timestamp()), [detail_serializer.data])
        else:
            objects = self.model.active_objects.filter(**model_filters)
            list_serializer = serializer_class(objects, many=True)
            # client is not consistent with server. So return 206 and combined with all data
            return build_etag_objects_response(str(model.updated_timestamp()), list_serializer.data,
                                               resp_status=status.HTTP_206_PARTIAL_CONTENT)


class EtagModelListMixin(object):
    """
    A mixin to check etag to determinate return updated models or whole models.
    """
    def list_response(self, etag, serializer_class, queryset, **model_filters):
        is_consistent = not etag or etag == INVALID_TAG
        new_etag = get_etag_from_model(self.model)
        if is_consistent:
            resp_status = status.HTTP_200_OK
        else:
            # client is not consistent with server. So return 206 and combined with all data
            queryset = self.model.active_objects.filter(**model_filters)
            resp_status = status.HTTP_206_PARTIAL_CONTENT
        list_serializer = serializer_class(queryset, many=True)
        return build_etag_objects_response(new_etag, list_serializer.data, resp_status=resp_status)


class AlbumCreateView(EtagCheckMixin, EtagModelMixin, CreateAPIView):
    """
    创建用户相册.

    如果成功创建, 返回相册对象. 如果etag和服务器不一致, 返回206以及所有的用户相册对象
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token. 参考LoginView
    返回: 如果数据一致返回200和创建的对象, 不一致返回206和对象列表

     etag -- 可选.通过url的parameter传递. 服务器通过etag检查来检查服务器和客户端是否一致.
    """
    permission_classes = (IsAuthenticated,)
    model = Album
    serializer_class = AlbumCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            serializer.object.user = self.request.user
            album = serializer.save()
            etag = self.check_etag(request)
            return self.detail_or_list_response(etag, AlbumSerializer, album, user=self.request.user)
        raise exceptions.ParseError(serializer.errors)


class AlbumDeleteView(EtagCheckMixin, EtagModelMixin, APIView):
    """
    删除用户相册.

    <font color=red>该API需要授权访问.</font> 调用者需要在http header中传递token. 参考LoginView
    返回: <ul><li>200成功</li><li>404相册不存在</li><li>206相册不一致</li></ul>

     etag -- 可选.通过url的parameter传递. 服务器通过etag检查来检查服务器和客户端是否一致. 如果数据一致返回200, 不一致返回206和对象列表
    """
    permission_classes = (IsAuthenticated,)
    model = Album

    def post(self, request, *args, **kwargs):
        try:
            album = Album.active_objects.get(id=kwargs.get('pk', None), user=request.user)
            album.deactivate()
            etag = self.check_etag(request)
            return self.detail_or_list_response(etag, AlbumSerializer, album, user=self.request.user)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AlbumImageListView(EtagCheckMixin, ListAPIView):
    """
    获取用户所有相片列表.
    <font color=red>该API需要授权访问.</font> 调用者需要在http header中传递token. 参考LoginView
    返回: <ul><li>200成功</li><li>404图片不存在</li></ul>

     etag -- 可选. 相册图片的etag, 通过上次接口返回. 通过url的parameter传递. 如果服务器通过etag检查没有变化, 返回304.<br> 如果不传递etag, 服务器返回所有对象
    """
    permission_classes = (IsAuthenticated,)
    model = AlbumImage
    serializer_class = AlbumImageSerializer

    def get(self, request, *args, **kwargs):
        etag = self.check_etag(request)
        if not etag:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        images = AlbumImage.active_objects.filter(user=request.user)
        serializer = self.serializer_class(images, many=True)
        return build_etag_objects_response(etag, serializer.data)


class AlbumImageUploadView(EtagCheckMixin, EtagModelMixin, CreateAPIView):
    """
    上传图片.
    图片通过form表单上传. 如果成功,返回头像图片的链接.
    注意: 客户端需要限制头像的大小.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token. 参考LoginView
    返回: 如果数据一致返回200和创建成功的对象, 不一致返回206和所有对象列表
    # 测试 command like below with httppie
    #   >> http -f POST 127.0.0.1:8020/api/album/1/image/upload/ "Authorization: Token 1" image@~/Downloads/1393169779_91.png

     etag -- 可选.通过url的parameter传递. 服务器通过etag检查来检查服务器和客户端是否一致.

    """
    serializer_class = AlbumImageCreateSerializer
    permission_classes = (IsAuthenticated,)
    model = AlbumImage

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA, files=request.FILES)
        if serializer.is_valid():
            serializer.object.user = self.request.user
            try:
                serializer.object.album = Album.active_objects.get(id=kwargs['album'])
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
            image = serializer.save()
            etag = self.check_etag(request)
            return self.detail_or_list_response(etag, AlbumImageSerializer, image, user=self.request.user)

        raise exceptions.ParseError(serializer.errors)


class AlbumImageDeleteView(EtagCheckMixin, EtagModelMixin, APIView):
    """
    删除图片.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token. 参考LoginView
    返回: 如果数据一致返回200, 不一致返回206和所有对象列表

     etag -- 可选.通过url的parameter传递. 服务器通过etag检查来检查服务器和客户端是否一致.
    """
    permission_classes = (IsAuthenticated,)
    model = AlbumImage

    def post(self, request, *args, **kwargs):
        try:
            image = AlbumImage.active_objects.get(id=kwargs.get('pk', None), user=request.user)
            image.deactivate()
            etag = self.check_etag(request)
            return self.detail_or_list_response(etag, AlbumImageSerializer, image, user=self.request.user)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AlbumImageBulkDeleteView(EtagCheckMixin, EtagModelListMixin, APIView):
    """
    批量删除图片.
    通过json数组指定要删除的图片id. 如下:
        [1,2,3]
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token. 参考LoginView
    返回: 如果数据一致返回200, 不一致返回206和所有对象列表
    测试: >> echo '[1,2,3]' | http -f --debug POST http://127.0.0.1:8020/api/album/image/bulk_delete/ "Authorization: Token 1" Content-Type:'application/json; charset=utf-8'

     etag -- 可选.通过url的parameter传递. 服务器通过etag检查来检查服务器和客户端是否一致.
    """
    permission_classes = (IsAuthenticated,)
    model = AlbumImage
    serializer_class = AlbumImageSerializer

    def post(self, request, *args, **kwargs):
        try:
            # XXX: have to make loop to touch the object one by one to fire the save() of model instead of update bulk
            for id in request.DATA:
                try:
                    image = AlbumImage.active_objects.only('is_active', 'image').get(id=id, user=request.user)
                    image.deactivate()
                except AlbumImage.DoesNotExist:
                    pass
            etag = self.check_etag(request)
            return self.list_response(etag, self.serializer_class,
                                      AlbumImage.objects.filter(id__in=request.DATA),
                                      user=self.request.user)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class JournalListView(EtagCheckMixin, ListAPIView):
    """
    获取用户游记.
    <font color=red>该API需要授权访问</font>. 调用者需要在http header中传递token. 参考LoginView

     etag -- 可选. 类别列表的etag, 通过上次接口返回. 通过url的parameter传递. 如果服务器通过etag检查没有变化, 返回304.<br> 如果不传递etag, 服务器返回所有数据
    """
    permission_classes = (IsAuthenticated,)
    model = Journal
    serializer_class = JournalSerializer

    def get(self, request, *args, **kwargs):
        etag = self.check_etag(request)
        if not etag:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        journal = Journal.active_objects.filter(creator=request.user)
        serializer = self.serializer_class(journal, many=True)
        return build_etag_objects_response(etag, serializer.data)


class JournalCreateView(EtagCheckMixin, EtagModelMixin, CreateAPIView):
    """
    创建或更新用户游记.

    如果上传的数据中id!=0,则更新游记, 否则创建游记
    如果成功创建或更新, 返回游记对象. 如果etag和服务器不一致, 返回206以及所有的用户相册对象
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token. 参考LoginView
    返回: 如果数据一致返回200和创建的对象, 不一致返回206和对象列表

     etag -- 可选.通过url的parameter传递. 服务器通过etag检查来检查服务器和客户端是否一致.
    """
    permission_classes = (IsAuthenticated,)
    model = Journal
    serializer_class = JournalCreateSerializer

    def post(self, request, *args, **kwargs):
        journal_id = request.DATA.get('id', 0)
        try:
            journal = Journal.active_objects.get(id=journal_id, creator=request.user) if journal_id != 0 else None
        except Journal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # For new journal we need delete 'id' from request.DATA
        if 'id' in request.DATA:
            del request.DATA['id']
        serializer = self.serializer_class(data=request.DATA, instance=journal)
        if serializer.is_valid():
            serializer.object.creator = self.request.user
            journal = serializer.save()
            etag = self.check_etag(request)
            return self.detail_or_list_response(etag, JournalSerializer, journal, creator=self.request.user)
        raise exceptions.ParseError(serializer.errors)


class JournalDeleteView(EtagCheckMixin, EtagModelMixin, APIView):
    """
    删除用户游记.

    <font color=red>该API需要授权访问.</font> 调用者需要在http header中传递token. 参考LoginView
    返回: <ul><li>200成功</li><li>404游记不存在</li><li>206游记不一致</li></ul>

     etag -- 可选.通过url的parameter传递. 服务器通过etag检查来检查服务器和客户端是否一致. 如果数据一致返回200, 不一致返回206和对象列表
    """
    permission_classes = (IsAuthenticated,)
    model = Journal

    def post(self, request, *args, **kwargs):
        try:
            journal = Journal.active_objects.get(id=kwargs.get('pk', None), creator=request.user)
            journal.deactivate()
            etag = self.check_etag(request)
            return self.detail_or_list_response(etag, JournalSerializer, journal, creator=self.request.user)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class JsonFileCacheResponseMixin(object):
    def json_file_content(self, file_name):
        cache = get_cache('default')
        content = cache.get(file_name + "_file")
        if content is None:
            if os.path.exists(file_name):
                with open(file_name, 'r') as f:
                    content = f.read().encode("utf-8")
            else:
                content = r'{"etags": "0", "objects":[]}'
            cache.set(file_name + "_file", content, CACHE_TIMEOUT_SEC)
        return content

    def json_file_response(self, file_name):
        content = self.json_file_content(file_name)
        return build_simple_json_response(content)


class ThirdpartyWebCamera(JsonFileCacheResponseMixin, APIView):

    def get(self, request, *args, **kwargs):
        return self.json_file_response(settings.THIRDPARTY_WEBCAMERA_FILE)


class ChatroomDetailMixin(object):
    def detail_response(self, chatroom):
        # self.request.user.customer
        detail = ChatroomSerializer(instance=chatroom, context={"user": self.request.user})
        return build_etag_objects_response(chatroom.get_etag(), [detail.data])


class ChatroomListView(ListAPIView):
    """
    获取用户所在聊天室列表.

    其中members的格式如下
    <pre>
        "members": [
            {
                "nick_name": "",
                "avatar_url": "",
                "id": 101,
                "name": "customer"
            }
            {
            ...
            },
        ]
    </pre>

    其中owner的格式如下
    <pre>
        "owner":  {
            "nick_name": "",
            "avatar_url": "",
            "id": 101,
            "name": "customer"
        }
    </pre>

    """
    permission_classes = (IsAuthenticated,)
    model = Chatroom
    serializer_class = ChatroomSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        chatrooms = Chatroom.active_objects.filter(members=user_id).prefetch_related("members", "owner")
        try:
            latest_obj = Chatroom.objects.filter(members=user_id).only('updated').latest()
            etag = latest_obj.get_etag()
        except:
            etag = INVALID_TAG
        serializer = self.serializer_class(chatrooms, many=True, context={"user": self.request.user})
        return build_etag_objects_response(etag, serializer.data)


class ChatroomCreateView(ChatroomDetailMixin, CreateAPIView):
    """
    创建或更新聊天室.

    如果上传的数据中id!=0,则更新聊天室, 否则创建聊天室. 只有聊天室的owner才可以更新聊天室.
    如果成功创建或更新, 返回聊天室对象.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token. 参考LoginView
    """
    permission_classes = (IsAuthenticated,)
    model = Chatroom
    serializer_class = ChatroomCreateSerializer

    def post(self, request, *args, **kwargs):
        chatroom_id = request.DATA.get('id', 0)
        try:
            chatroom = Chatroom.active_objects.prefetch_related("members", "owner").\
                get(id=chatroom_id, owner=request.user.customer) if chatroom_id != 0 else None
        except Journal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # For new chatroom we need delete 'id' from request.DATA
        if 'id' in request.DATA:
            del request.DATA['id']
        serializer = self.serializer_class(data=request.DATA, instance=chatroom)
        if serializer.is_valid():
            serializer.object.creator = self.request.user.customer
            serializer.object.owner = self.request.user.customer
            chatroom = serializer.save()
            # add customer to the chatroom as a member in case of create
            if not chatroom_id:
                chatroom.members.add(self.request.user.customer)
            return self.detail_response(chatroom)

        raise exceptions.ParseError(serializer.errors)


class ChatroomJoinView(ChatroomDetailMixin, CreateAPIView):
    """
    加入聊天室.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token.

    如果加入成功, 返回聊天室对象.
    如果verify_code验证不通过，返回失败信息。
    如果当前用户已在该聊天室的黑名单中，返回失败信息。
    """
    permission_classes = (IsAuthenticated,)
    model = Chatroom
    serializer_class = ChatroomJoinSerializer

    def post(self, request, *args, **kwargs):
        try:
            # XXX: can't prefetch_related member here, it will cache the members and
            # return staled member even has add a new member
            chatroom = Chatroom.active_objects.only('updated', 'verify_code', 'black_list').get(id=kwargs.get('pk', None))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.DATA, context={"chatroom": chatroom,
                                                                       "user": request.user.customer})
        if serializer.is_valid():
            chatroom.add_member(self.request.user.customer)
            # call save to make sure the updated is updated after member changed.
            chatroom.save(update_fields=['updated'])
            chatroom = Chatroom.active_objects.prefetch_related("members", "owner").get(id=kwargs.get('pk', None))
            return self.detail_response(chatroom)
        raise exceptions.ParseError(serializer.errors)


class ChatroomLeaveView(ChatroomDetailMixin, APIView):
    """
    离开聊天室.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token.

    如果离开成功, 返回聊天室对象.
    """
    permission_classes = (IsAuthenticated,)
    model = Chatroom

    def post(self, request, *args, **kwargs):
        try:
            # XXX: can't prefetch_related member here, it will cache the members and
            # return staled member even has remove a old member
            chatroom = Chatroom.active_objects.only('updated').get(id=kwargs.get('pk', None))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        chatroom.remove_member(self.request.user.customer)
        # call save to make sure the updated is updated after member changed.
        chatroom.save(update_fields=['updated'])
        chatroom = Chatroom.active_objects.prefetch_related("members", "owner").get(id=kwargs.get('pk', None))

        return self.detail_response(chatroom)


class ChatroomMessageListView(CreateAPIView):
    """
    返回指定聊天室的消息列表.

    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token.

    传入参数：
    <pre>
    [
        {
            "chatroom_id": 聊天室id,
            "etag": 服务器端返回的最后一次聊天室消息的etag. 如果没有, 传入空
        },
        {
         ...
        }
    ]
    </pre>

    发送成功后, 服务器会返回每个房间未收到的消息列表.
    消息列表格式如下:
    <pre>
    [
        {
            "chatroom_id": 2,
            "etag": "1397909279334",
            "messages": [
                {
                    "content": "Hello everyone!",
                    "timestamp": 1397908596554,
                    "type": 0,
                    "id": "31dGBd1Cqq",
                    "sender": {
                        "nick_name": "",
                        "avatar_url": "",
                        "id": 101,
                        "name": "customer"
                    }
                },
                {
                ...
                },
            ]
        }
    ]
    </pre>
    其中:
    <ol>
     <li>id 消息的唯一id. 客户端需要通过该id来处理重复消息.</li>
     <li>timestamp 是消息的创建时间.单位毫秒</li>
     <li> type 是消息类型.  0->普通消息 1->新成员加入聊天室 2->成员离开聊天室.</li>
    </ol>
    测试：curl -H "Authorization:Token 1" -H "Content-Type:application/json; charset=utf-8" -d '[{"chatroom_id":1, "etag": ""}]' http://localhost:8000/api/chatroom/messages/
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatroomMessageListSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA, many=True)
        if serializer.is_valid():
            messages = Chatroom.objects.retrieve_messages(serializer.data)
            return build_simple_json_response(data=messages)
        raise exceptions.ParseError(serializer.errors)


class ChatroomMessageCreateView(CreateAPIView):
    """
    发送聊天室消息.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token.

    参数：
    <pre>
    {
        "content": "消息内容"
    }
    </pre>

    发送成功后, 服务器会返回当前房间未收到的消息列表.包括当前创建的消息.
    测试：
    curl -H "Authorization:Token 1" -H "Content-Type:application/json; charset=utf-8" -d '{"content":"Hello everyone!"}' http://localhost:8000/api/chatroom/1/message/create/

    etag -- 可选.服务器端返回的最后一次聊天室消息的etag. 如果没有, 传入空
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatroomMessageSerializer

    def post(self, request, *args, **kwargs):
        try:
            chatroom = Chatroom.active_objects.get(id=kwargs.get('pk', None))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            etag = chatroom.get('etag', '')
            if etag == '':
                etag = int(time.time() * 1000)
            chatroom.send_message(serializer.data['content'], Chatroom.MESSAGE_TYPE_TEXT, request.user.customer)
            messages = chatroom.retrieve_messages(etag)
            return build_simple_json_response("[%s]" % messages)
        raise exceptions.ParseError(serializer.errors)


class ChatroomBlockUsersView(ChatroomDetailMixin, APIView):
    """
    添加黑名单.
    <font color=red>该API需要授权访问</font> 调用者需要在http header中传递token.

    参数：
    <pre>
    [需列入黑名单的用户id]
    </pre>

    如果传入的用户是该聊天室的所有者，则返回错误信息。
    如果成功创建或更新, 返回聊天室对象。

    测试：curl -H "Authorization:Token 1" -H "Content-Type:application/json; charset=utf-8" -d '[102]' http://localhost:8000/api/chatroom/1/block_users/
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            chatroom = Chatroom.active_objects.get(id=kwargs.get('pk', None))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        new_ids = request.DATA
        if chatroom.owner.id in new_ids:
            raise exceptions.NotAcceptable(detail=u'不能将聊天室所有者加入黑名单')
        chatroom.add_blocked_users(new_ids)
        chatroom.save(update_fields=['black_list'])
        return self.detail_response(chatroom)
