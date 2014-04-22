#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from django.conf import settings
from django.core.management import BaseCommand
import redis

from apps.chatroom.models import Chatroom


class Command(BaseCommand):
    """
    a command to clean the timeout messages in redis.
    schedule it at crotab every hour like below
    crontab -e
        0 * * * * workon django-tourguide && cd /opt/www/django-tourguide/src/ && python manage.py clean_chatroom_messages >> /var/log/django-tourguide.log 2>&1
    """
    help = "clean up the timeout messages in chatroom"

    def handle(self, *args, **options):
        connection = redis.Redis()
        p = connection.pipeline(transaction=False)
        for chatroom in Chatroom.objects.all():
            until_score = (int(time.time()) - settings.CHATROOM_MESSAGE_TIMEOUT_SEC) * 1000
            p.zremrangebyscore(chatroom.get_redis_key(), "-inf",  until_score)
        print p.execute()
