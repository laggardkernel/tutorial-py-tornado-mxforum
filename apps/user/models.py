#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from peewee import CharField, TextField
from peewee_extra_fields import SimplePasswordField as PasswordField
from mxforum.models import BaseModel

GENDERS = (("female", "女"), ("male", "男"))
# python -c "import uuid; print(uuid.uuid4())"
SALT = "b61ce065-be80-4c15-a24c-a526e40d483f"


class User(BaseModel):
    mobile = CharField(max_length=11, verbose_name="手机号码", index=True, unique=True)
    # password field is removed from peewee, get it from peewee_extra_fields
    # PasswordField auto hash the input string with salt
    password = PasswordField(salt=SALT, verbose_name="密码")
    nickname = CharField(max_length=64, verbose_name="昵称", null=True)
    avatar = CharField(max_length=256, null=True, verbose_name="头像")
    address = CharField(max_length=256, null=True, verbose_name="地址")
    profile = TextField(null=True, verbose_name="个人简介")
    gender = CharField(max_length=10, choices=GENDERS, null=True, verbose_name="性别")

    class Meta:
        # db_table for peewee 2.x, table_name for 3.x
        # peewee-async 0.5.12 still requires 2.x, use the pre-release 0.6+
        # db_table = "users"
        table_name = "users"
