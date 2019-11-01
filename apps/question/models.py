#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import os
import uuid
import aiofiles
from peewee import CharField, TextField, ForeignKeyField, IntegerField, JOIN
from mxforum.settings import settings
from mxforum.models import BaseModel
from apps.user.models import User


class Question(BaseModel):
    class Meta:
        table_name = "questions"

    user = ForeignKeyField(User, verbose_name="楼主", backref="questions")
    category = CharField(max_length=64, verbose_name="分类", null=False)
    title = CharField(max_length=256, verbose_name="标题", null=False)
    body = TextField(verbose_name="内容", null=False)
    # 问题图片是否为必需，非必需。还有就是这里限制了只能添加一张图片
    image = CharField(max_length=256, verbose_name="图片", null=True)
    answer_num = IntegerField(default=0, verbose_name="回答数")

    @staticmethod
    def __hash_filename(filename):
        """Generate a random name for uploaded file"""
        # 由于 werkzeug.secure_filename 不支持中文，所以没必要使用
        _, _, extension = filename.rpartition(".")
        return "%s.%s" % (uuid.uuid4().hex, extension)

    @staticmethod
    async def save_image(uploaded_file):
        filename = __class__.__hash_filename(uploaded_file["filename"])
        file_path = os.path.join(settings["media_root"], filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(uploaded_file["body"])
        return filename

    @property
    def image_url(self):
        return "{}/media/{}".format(settings["site_url"], self.image)

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nickname, User.mobile).join(User)


class Answer(BaseModel):
    """既代表问题的回答，也代表对于另外一个回答的回复: answer and reply"""

    class Meta:
        table_name = "answers"

    user = ForeignKeyField(User, verbose_name="用户", backref="answers")
    question = ForeignKeyField(
        Question, verbose_name="问题", backref="answers", null=True
    )
    answered = ForeignKeyField(
        "self", verbose_name="回复此评论", backref="replies", null=True
    )
    # replied 属于冗余存储，但是可以减少表的查询压力
    replied = ForeignKeyField(
        User, verbose_name="回复此人", backref="answer_replies", null=True
    )
    body = CharField(max_length=1024, verbose_name="回复内容", null=False)
    reply_num = IntegerField(default=0, verbose_name="回复数")

    @classmethod
    def extend(cls):
        # 多表join
        # 多字段映射同意个Model
        # alias
        user = User.alias()
        replied = User.alias()
        return (
            cls.select(
                cls,
                Question,
                user.id,
                user.nickname,
                user.mobile,
                replied.id,
                replied.nickname,
                replied.mobile,
            )
            .join(Question, join_type=JOIN.LEFT_OUTER, on=cls.question)
            .switch(cls)
            .join(user, join_type=JOIN.LEFT_OUTER, on=cls.user)
            .switch(cls)
            .join(replied, join_type=JOIN.LEFT_OUTER, on=cls.replied)
        )
