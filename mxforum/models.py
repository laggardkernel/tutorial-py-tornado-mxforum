#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from datetime import datetime
from peewee import Model
from peewee import DateTimeField
from mxforum.settings import database


class BaseModel(Model):
    created_time = DateTimeField(default=datetime.utcnow, verbose_name="创建时间")

    class Meta:
        database = database
