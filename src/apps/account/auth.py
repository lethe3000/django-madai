#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
from django.contrib.auth.hashers import MD5PasswordHasher
from django.utils.encoding import force_bytes
from utils.random import gen_random_string


class Hao3sMD5PasswordHasher(MD5PasswordHasher):
    """
    由于好川味平台现有大量用户帐号，密码存储及登录验证均采用MD5+salt方式，具体算法较为特殊，因此要打通E游平台与好川味平台帐号，
    E游平台帐号的MD5加密方式须使用好川味相同的方式。
    好川味MD5Password = md5(md5(password)+salt)
    算法说明：
    1. 先对明文密码md5一次，然后将salt盐值串接在后面，再md5一次；
    2. salt字符串长度介于4～6位；
    3. md5后的字符串为小写字符串；
    举例：
    明文密码：602431
    Salt盐值：2368
    最终Md5值：b0026674b8f076f8cd65c3a6eb511f1c
    """
    algorithm = "hao3smd5"

    def encode(self, password, salt):
        assert password
        assert salt and '$' not in salt
        md5_1 = hashlib.md5(force_bytes(password)).hexdigest()
        hash = hashlib.md5(md5_1 + salt).hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, hash)

    def salt(self):
        """
        Generates a cryptographically secure nonce salt in ascii
        """
        return gen_random_string(size=6)
