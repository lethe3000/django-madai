#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from django.db import models
from django.conf import settings
import time
import redis
from apps.common.models import BaseModel
from apps.customer.models import Customer
from utils.random import gen_random_string

pool = redis.ConnectionPool(host=settings.REDIS_SERVER_IP, port=settings.REDIS_SERVER_PORT, db=0)


class ChatroomManager(models.Manager):

    def retrieve_messages(self, chatrooms):
        connection = redis.Redis(connection_pool=pool)
        p = connection.pipeline(transaction=False)
        for chatroom in chatrooms:
            key = "chatroom_%s" % chatroom['chatroom_id']
            etag = chatroom.get('etag', '')
            if etag == '':
                etag = int(time.time() * 1000)
            p.zrangebyscore(key, "(%s" % etag, "+inf", withscores=True)
        all_chatroom_message = p.execute()
        res = ""
        for i, chatroom_messages in enumerate(all_chatroom_message):
            # the format of chatroom_messages like below
            #  [(message, score),(...)] => [("adfadf", 12345), ("adfdf", 4567)]
            # use the score of last item as the etag.
            if chatroom_messages:
                etag = int(chatroom_messages[-1][1])
                json_text = '{"chatroom_id": %d, "etag": "%d", "messages":[%s]}' % \
                            (chatrooms[i]["chatroom_id"], etag,
                             ",".join([message for (message, _) in chatroom_messages]))
            else:
                # return a default data even this chatroom has no data.
                json_text = '{"chatroom_id": %d, "etag": "%d", "messages":[]}' % \
                            (chatrooms[i]["chatroom_id"], int(time.time() * 1000))

            if res:
                res += "," + json_text
            else:
                res = json_text
        return "[%s]" % res


class Chatroom(BaseModel):

    MESSAGE_TYPE_TEXT = 0
    MESSAGE_TYPE_CHATROOM_JOIN = 1
    MESSAGE_TYPE_CHATROOM_LEAVE = 2

    name = models.CharField(max_length=128,
                            verbose_name=u'标题',
                            default="",
                            blank=False)

    description = models.CharField(max_length=512,
                                   verbose_name=u'描述',
                                   default="",
                                   blank=True)

    members = models.ManyToManyField(Customer,
                                     verbose_name=u'成员',
                                     related_name='chatrooms')

    verify_code = models.CharField(max_length=32,
                                   verbose_name=u'验证码',
                                   default='',
                                   blank=True)

    black_list = models.TextField(verbose_name=u'黑名单',
                                  default='',
                                  blank=True)

    objects = ChatroomManager()

    def get_etag(self):
        return str(self.updated_timestamp())

    def __unicode__(self):
        return self.name


    class Meta:
        verbose_name = u"聊天室"
        ordering = ('-updated',)
        get_latest_by = "updated"

    def get_redis_key(self):
        return "chatroom_%s" % self.id

    def add_member(self, member):
        self.members.add(member)
        # send join event
        self.send_message('', self.MESSAGE_TYPE_CHATROOM_JOIN, member)

    def remove_member(self, member):
        self.members.remove(member)
        # send leave event
        self.send_message('', self.MESSAGE_TYPE_CHATROOM_LEAVE, member)

    def add_blocked_users(self, blocked_users):
        # blocked_users 为customer id所组成的list
        black_list_text = ','.join([str(id) for id in blocked_users])
        if self.black_list:
            self.black_list += ',' + black_list_text
        else:
            self.black_list = black_list_text

        for customer in Customer.objects.filter(id__in=blocked_users).all():
            self.remove_member(customer)

    def send_message(self, message, message_type, sender):
        # 把message的各种信息存到redis中
        # {
        #   id
        #   type,
        #   content,
        #   timestamp,
        #   sender: {"id", "name", "nick_name", "avatar_url"},
        # }

        sender_info = {"id": sender.id, "name": sender.name, "nick_name": sender.nick_name, "avatar_url": sender.avatar_url()}
        body = {"id":  gen_random_string(10), "content": message, "type": message_type,
                "sender": sender_info, "timestamp": int(time.time() * 1000)}
        score = body["timestamp"]
        connection = redis.Redis(connection_pool=pool)
        connection.zadd(self.get_redis_key(), json.dumps(body), score)

    def retrieve_messages(self, etag):
        connection = redis.Redis(connection_pool=pool)
        messages = connection.zrangebyscore(self.get_redis_key(), "(%s" % etag, "+inf", withscores=True)
        # use the timestamp of last one as the etag
        etag = int(messages[-1][1])
        return '{"chatroom_id": %d, "etag":"%s", "messages":[%s]}' % (self.id, etag,
                                                                      ",".join([message for (message, _) in messages]))
