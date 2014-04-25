#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.cache import get_cache
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

CACHE = get_cache('default')
INVALID_ETAG = "0"
CACHE_TIMEOUT_SEC = 1 * 60 * 60

@receiver(post_save)
def handle_db_updated(sender, instance=None, created=False, **kwargs):
    """
    observe the change of db and clean up the cache
    """
    if hasattr(sender, 'cache_objects'):
        sender.cache_objects.clean_cache_for_model(instance)


class UserAwareCacheMixin(object):
    user_field_name = "creator"


class SimpleCacheManager(models.Manager):
    """
    a simple cache manager to cache data associated with user id.
    It means associate to all of users if user id is 0
    """
    def get_cache_key_objects(self, user_id=0):
        return "model-%s-objects-%s" % (self.model._meta.object_name.lower(), user_id)

    def get_cache_key_etag(self, user_id=0):
        return "model-%s-etag-%s" % (self.model._meta.object_name.lower(), user_id)

    def clean_cache_for_model(self, model_instance):
        user_id = 0
        if isinstance(self.model, UserAwareCacheMixin):
            user_id = model_instance[self.model.user_field_name]
        CACHE.delete(self.get_cache_key_objects(user_id))
        CACHE.delete(self.get_cache_key_etag(user_id))

    def get_etag(self, user_id=0, **filters):
        etag = CACHE.get(self.get_cache_key_etag(user_id))
        if not etag:
            try:
                # XXX: intend not to use active_objects. we should consider the deactive object as etag value.
                latest_obj = self.filter(**filters).only('updated').latest()
                etag = latest_obj.get_etag()
            except self.model.DoesNotExist:
                etag = INVALID_ETAG
            CACHE.set(self.get_cache_key_etag(), etag, CACHE_TIMEOUT_SEC)
        return etag

    def get_objects(self, user_id=0, cache_missing_callback=None):
        data = CACHE.get(self.get_cache_key_objects(user_id))
        if not data and cache_missing_callback:
            data = cache_missing_callback()
            self.set_objects(data)
        return data

    def set_objects(self, objects, user_id=0):
        CACHE.set(self.get_cache_key_objects(user_id), objects, CACHE_TIMEOUT_SEC)
