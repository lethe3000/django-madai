#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import get_cache
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import requests

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from apps.chatroom.models import Chatroom
from apps.customer.models import Customer, Journal
from apps.foundation.models import ClientApp, OS_TYPE_ANDROID
from apps.imagestore.models import Album, AlbumImage
from apps.tour.models import Scenery, GuideType, Article
from utils.random import gen_random_string

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))

CACHE_TIMEOUT_SEC = 5 * 60 # 5 minutes

class ZeroIntegerField(serializers.IntegerField):
    def to_native(self, obj):
        return obj if obj else 0


class DefaultBooleanField(serializers.BooleanField):
    def to_native(self, obj):
        return obj if obj else False


class ScenerySerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source='image_url')

    class Meta:
        model = Scenery
        fields = ('id', "name", "image_url", "summary", "display_order", "is_virtual", 'phone_contact', 'phone_sos', 'thirdparty_id')


class GuideTypeSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source='image_url')

    class Meta:
        model = GuideType
        fields = ('id', "name", "image_url", "summary",  "display_order")


class ArticleSerializer(serializers.ModelSerializer):
    title_image_url = serializers.CharField(source='title_image_url')
    content_url = serializers.URLField(source='content_url')
    created = serializers.IntegerField(source='created_timestamp')
    updated = serializers.IntegerField(source='updated_timestamp')

    class Meta:
        model = Article
        fields = ('id', "title", "title_image_url", "content_url", "created", "updated",
                  "web_link", "is_pinned", "summary", "scenery", "guide_type", "desc", "source")


class Hao3sMixin(object):
    def has_username_in_hao3s(self, username):
        """
        检查好川味是否存在指定的账号
        """
        return self.retrieve_password_hash_from_hao3s(username)

    def retrieve_password_hash_from_hao3s(self, username):
        """
        获取账号名称返回salt和md5 hash

        好川味接口Url:
        http://m.hao3s.com/api/check_user.php
        Post json：
        {"username": "xxxxx"}
        其中username为待注册的用户名字符串
        Resp json：
        {"code": "1", "username": "xxxxx", "md5": "xxx", "salt": "xxx"}
        code: 1--帐号存在, 同时返回该用户在好川味注册的密码的md5值以及salt值；
              0--帐号不存在,同时返回msg字符串
              -1—输入username为空

        """
        url = 'http://m.hao3s.com/api/check_user.php'
        logger.debug("access " + url + " to check username " + username)
        r = requests.post(url, data=('{"username": "%s"}' % username), headers={"content-type": "application/json; charset=utf-8"})
        # make sure this username is not exist in hao3s
        # ignore any errors and let local register move on.
        if r.status_code == 200:
            try:
                data = json.loads(r.text)
                if int(data['code']) == 1:
                    return "hao3smd5$%s$%s" % (data['salt'], data['md5'])
                else:
                    return ''
            except:
                logger.error("[hao3s]get error for access " + url + " to check username " + username)
        return "dummy"

    def sync_account_to_hao3s(self, username, password):
        """
        将账号信息同步到好川味.

        好川味接口Url:
        http://m.hao3s.com/api/sync_user.php
        Post json：
        {"username": "xxxxx", "md5": "xxxxx", "salt": "xxxxx"}
        其中：
        username为待同步的用户名字符串
        md5 为md5(md5(password)+salt)之后的字符串
        salt 为md5单向加密的盐值
        Resp json：
        {"code": 1, "msg": "同步帐号成功"}
        code: 1--同步帐号成功,
             0--同步帐号失败，
            -1--username为空
            -2--md5为空
            -3--salt为空
            -4—username已存在
        """
        # the hash format got from make_password like
        #   "md5$dadfdf$xxxxxhash"
        # so we only concern the last segment.
        url = 'http://m.hao3s.com/api/sync_user.php'
        logger.debug("access " + url + " to sync username " + username)
        if password.startswith('hao3smd5$'):
            # just use it if it's encoded already
            salt = password.split("$")[1]
            md5_hash = password.split("$")[2]
        else:
            # encode the password first if it's raw password.
            salt = gen_random_string(size=6)
            md5_hash = make_password(password, salt=salt, hasher='hao3smd5').split('$')[2]
        data = {'username': username, 'md5': md5_hash, 'salt': salt}
        r = requests.post(url, data=json.dumps(data), headers={"content-type": "application/json; charset=utf-8"})
        res = False
        if r.status_code == 200:
            logger.debug("[hao3s]sync_user response \n" + r.text)
            res = int(json.loads(r.text)['code']) == 1
        if not res:
            logger.error("[hao3s]get error for access " + url + " to sync username " + username)
        return res


class AuthTokenSerializer(Hao3sMixin, serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def create_user_if_need(self, username, password):
        """
        如果账户在本地不存在, 我们需要到去好川味去检查该账号, 如果账号和密码匹配会自动在本地创建该账号.
        """
        try:
            user = get_user_model().objects.get(name=username)
        except get_user_model().DoesNotExist:
            hao3s_password_hash = self.retrieve_password_hash_from_hao3s(username)
            if not check_password(password, hao3s_password_hash):
                raise serializers.ValidationError(u"登录信息不正确")
            # 自动创建该账号
            customer = Customer(name=username,
                                is_staff=False,
                                is_active=True,
                                is_imported_from_thirdparty=True,
                                has_sync_to_thirdparty=True)
            customer.set_password(password)
            customer.save()
            Token.objects.get_or_create(user=customer)
            return customer
        return None

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError(u'请输入完整的账号信息')

        self.create_user_if_need(username, password)
        user = authenticate(username=username, password=password)

        if user:
            if not user.is_active:
                raise serializers.ValidationError(u'账号已经被冻结')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(u"登录信息不正确")


class RegisterSerializer(Hao3sMixin, serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField(required=False)
    nick_name = serializers.CharField(required=False)

    def validate(self, attrs):
        username = attrs.get('username')
        customer = Customer.objects.filter(name=username)
        if customer:
            raise serializers.ValidationError(u'用户名已经被使用')

        if self.has_username_in_hao3s(username):
            raise serializers.ValidationError(u'用户名已经被使用')

        password = attrs.get('password')
        sync_success = self.sync_account_to_hao3s(username, password)
        new_customer = Customer(is_active=True,
                                is_staff=False,
                                name=username,
                                email=attrs.get('email', ""),
                                nick_name=attrs.get('nick_name', ""),
                                has_sync_to_thirdparty=sync_success)
        new_customer.set_password(password)
        new_customer.save()
        token, created = Token.objects.get_or_create(user=new_customer)
        attrs['token'] = token.key
        return attrs


@receiver(post_save, sender=Customer)
def handle_customer_updated(sender, instance=None, created=False, **kwargs):
    """
    observe the change of customer and sync the password to hao3s
    """
    # do nothing if this customer is created instead of updated
    customer = instance
    if created or not customer.is_password_changed:
        return
    sync_success = Hao3sMixin().sync_account_to_hao3s(customer.name, customer.password)
    Customer.objects.filter(id=customer.id).update(has_sync_to_thirdparty=sync_success)
    # 更新token. 客户端才有机会重新刷新密码.
    logger.debug("reset the auth token due to password changed for " + customer.name)
    customer.auth_token.save()


class CustomAvatarSerializer(serializers.ModelSerializer):
     avatar = serializers.ImageField(source="avatar_file")

     class Meta:
        model = Customer
        fields = ("avatar",)


class CustomProfileDetailSerializer(serializers.ModelSerializer):
     avatar = serializers.CharField(source="avatar_url",
                                    required=False)

     class Meta:
        model = Customer
        fields = ("name", "avatar", "email", "nick_name", "phone", "gender", "address", "signature")


class CustomProfileUpdateSerializer(serializers.ModelSerializer):
     class Meta:
        model = Customer
        fields = ("email", "nick_name", "phone", "gender", "address", "signature")


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        customer = Customer.objects.filter(email=email)
        if not customer:
            raise serializers.ValidationError(u'邮件不存在.')
        return attrs


class AlbumSerializer(serializers.ModelSerializer):
    created = serializers.IntegerField(source='created_timestamp')

    class Meta:
        model = Album
        fields = ("id", "name", "created")


class AlbumCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Album
        fields = ("name",)


class AlbumImageSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="image.url")
    created = serializers.IntegerField(source='created_timestamp')

    class Meta:
        model = AlbumImage
        fields = ("id", "url", "created", "album")


class AlbumImageCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = AlbumImage
        fields = ("image", )


class ClientAppSerializer(serializers.ModelSerializer):
    download_url = serializers.CharField(source="download_url")

    class Meta:
        model = ClientApp
        fields = ("app_version_code", "app_version_name", "download_url", "is_force_upgrade")


class JournalSerializer(serializers.ModelSerializer):
    created = serializers.IntegerField(source='created_timestamp')
    updated = serializers.IntegerField(source='updated_timestamp')

    class Meta:
        model = Journal
        fields = ("id", "title", "content", "created", "updated")


class JournalCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='id', required=False)

    class Meta:
        model = Journal
        fields = ("id", "title", "content")


class CheckinSerializer(serializers.Serializer):
    etags = serializers.SerializerMethodField('get_etags')
    clientapp = serializers.SerializerMethodField('get_clientapp')

    def get_etags(self, obj):
        models = (("scenery", Scenery), ("guidetype", GuideType), ("article", Article))
        res = [{"model": item[0], "value": str(item[1].objects.only('updated').latest().updated_timestamp())} for item in models]
        # get etag from model aware of user
        user = self.context.get('user')
        user_aware_models = (("album", Album, {"user": user}),
                             ("albumimage", AlbumImage, {"user": user}),
                             ('journal', Journal, {"creator": user}))
        if user and user.id:
            res.append({"model": "myprofile", "value": str(user.customer.updated_timestamp())})
            try:
                latest_chatroom = Chatroom.objects.filter(members=user.id).only('updated').latest()
                res.append({"model": 'chatroom', "value": latest_chatroom.get_etag()})
            except Chatroom.DoesNotExist:
                pass

            for item in user_aware_models:
                try:
                    res.append({"model": item[0], "value": str(item[1].objects.only('updated').filter(**item[2]).latest().updated_timestamp())})
                except item[1].DoesNotExist:
                    pass

        # get etag from json file
        json_file_models = (('webcamera', settings.THIRDPARTY_WEBCAMERA_FILE),)
        for item in json_file_models:
            res.append({"model": item[0], "value": self.get_etags_from_json_file(item[1])})
        return res

    def get_etags_from_json_file(self, file_name):
        cache = get_cache('default')
        etag = cache.get(file_name + "_etag")
        if etag is None:
            if os.path.exists(file_name):
                with open(file_name, 'r') as f:
                    etag = json.loads(f.read().encode("utf-8"))['etag']
            else:
                etag = "0"
            cache.set(file_name + "_etag", etag, CACHE_TIMEOUT_SEC)
        return etag

    def get_clientapp(self, obj):
        if self.context.get('os', OS_TYPE_ANDROID) == OS_TYPE_ANDROID:
            app = ClientApp.objects.get_latest_android_app()
        else:
            app = ClientApp.objects.get_latest_ios_app()
        return ClientAppSerializer(instance=app).data


class ChatroomMemberSerializer(serializers.ModelSerializer):
    avatar_url = serializers.CharField(source='avatar_url')

    class Meta:
        model = Customer
        fields = ("id", "name", "nick_name", "avatar_url")


class ChatroomSerializer(serializers.ModelSerializer):
    owner = ChatroomMemberSerializer(source="owner.customer")
    members = ChatroomMemberSerializer(source="members", many=True)
    created = serializers.IntegerField(source='created_timestamp')
    updated = serializers.IntegerField(source='updated_timestamp')

    def to_native(self, obj):
        ret = super(ChatroomSerializer, self).to_native(obj)
        ret['is_owner'] = self.context['user'].id == obj.owner.id
        return ret

    class Meta:
        model = Chatroom
        fields = ("id", "name", "verify_code", "description", "owner", "members", "updated", "created")


class ChatroomCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chatroom
        fields = ("id", "name", "verify_code", "description")


class ChatroomJoinSerializer(serializers.Serializer):
    verify_code = serializers.CharField(u'验证码', required=True)

    def validate(self, attrs):
        if self.context['chatroom'].verify_code != attrs.get('verify_code'):
            raise serializers.ValidationError(u'验证码不正确.')
        black_list = self.context['chatroom'].black_list
        user = self.context['user']
        if black_list and (str(user.id) in black_list.split(',')):
            raise serializers.ValidationError(u'用户[%s]被禁止进入该聊天室.' % user.name)
        return attrs

    class Meta:
        fields = ("verify_code", )


class ChatroomMessageListSerializer(serializers.Serializer):
    chatroom_id = serializers.IntegerField(u'聊天室id')
    etag = serializers.CharField(u'服务器最后一次返回的聊天室消息的etag',
                                 blank=True)


class ChatroomMessageSerializer(serializers.Serializer):
    content = serializers.CharField(u'消息内容')
