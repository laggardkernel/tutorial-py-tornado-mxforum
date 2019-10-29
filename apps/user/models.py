#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from peewee import CharField, TextField
from werkzeug.security import generate_password_hash, check_password_hash
from mxforum.models import BaseModel

GENDERS = (("female", "女"), ("male", "男"))


class User(BaseModel):
    mobile = CharField(max_length=11, verbose_name="手机号码", index=True, unique=True)
    # password field is removed from peewee, get it from peewee_extra_fields
    # PasswordField auto hash the input string with salt
    password_hash = CharField(max_length=128, verbose_name="密码")
    nickname = CharField(max_length=64, verbose_name="昵称", null=True)
    avatar = CharField(max_length=256, null=True, verbose_name="头像")
    address = CharField(max_length=256, null=True, verbose_name="地址")
    profile = TextField(null=True, verbose_name="个人简介")
    gender = CharField(max_length=10, choices=GENDERS, null=True, verbose_name="性别")

    @property
    def password(self):
        """use @property decorator to password func as a prop of Role class"""
        raise AttributeError("password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    class Meta:
        # db_table for peewee 2.x, table_name for 3.x
        # peewee-async 0.5.12 still requires 2.x, use the pre-release 0.6+
        # db_table = "users"
        table_name = "users"
