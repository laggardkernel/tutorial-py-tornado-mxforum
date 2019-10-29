#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from tornado.web import RequestHandler
import aiofiles

from mxforum.handlers import RedisHandler
from apps.utils.decorators import authenticated
from apps.community.models import Group
from apps.community.forms import GroupForm


class GroupHandler(RedisHandler):
    @authenticated
    async def get(self, *args, **kwargs):
        pass

    @authenticated
    async def post(self, *args, **kwargs):
        r = {}
        # 不能使用JSON Form，前端传递封面文件时必须传递表单
        form = GroupForm(self.request.body_arguments)
        if form.validate():
            # 自实现图片字段（文件）验证，WTForms没有支持
            files_meta = self.request.files.get("front_image", None)
            if files_meta is None:
                self.set_status(400)
                r["front_image"] = "请设置小组图片"
            else:
                # 保存图片, I/O
                filename = ""
                for meta in files_meta:
                    filename = await Group.save_front_image(meta)
                group = await self.application.objects.create(
                    Group,
                    creator=self.current_user,
                    name=form.name.data,
                    category=form.category.data,
                    desc=form.desc.data,
                    notice=form.notice.data,
                    front_image=filename,
                )
                r["id"] = group.id
        else:
            self.set_status(400)
            for field in form.errors:
                r[field] = form.errors[field][0]
        self.finish(r)
