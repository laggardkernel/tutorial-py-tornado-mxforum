#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import json
from tornado.web import RequestHandler
from playhouse.shortcuts import model_to_dict

from mxforum.handlers import BaseHandler
from apps.utils.decorators import authenticated
from apps.utils.serializers import datetime2json
from apps.user.models import User
from apps.question.models import Question, Answer
from apps.question.forms import QuestionForm


class QuestionHandler(BaseHandler):
    async def get(self, *args, **kwargs):
        """获取问题"""
        r = []
        # 获取问题列表
        r = []
        # extend() is a custom method to do a join query with User
        query = Question.extend()

        # 根据组/社区类别做过滤
        category = self.get_argument("c", None)  # c for category
        if category:
            query = query.filter(Question.category == category)

        # 根据参数进行排序
        order = self.get_argument("o", "new")  # o for order
        if order and order == "hot":
            query = query.order_by(Question.member_num.desc())
        elif order == "new":
            query = query.order_by(Question.created_time.desc())
        questions = await self.application.objects.execute(query)
        for question in questions:
            item = model_to_dict(question)
            item["image"] = question.image_url
            r.append(item)

        self.finish(json.dumps(r, default=datetime2json))

    @authenticated
    async def post(self, *args, **kwargs):
        """添加问题"""
        r = {}
        # 不能使用JSON Form，前端传递封面文件时必须传递表单
        form = QuestionForm(self.request.body_arguments)
        if form.validate():
            # 自实现图片字段（文件）验证，WTForms没有支持，图片可选
            files_meta = self.request.files.get("image", None)
            filename = ""
            if files_meta:
                for meta in files_meta:
                    filename = await Question.save_image(meta)
                    break
            question = await self.application.objects.create(
                Question,
                user=self.current_user,
                category=form.category.data,
                title=form.title.data,
                body=form.body.data,
                image=filename,
            )
            r["id"] = question.id
            self.set_status(201)
        else:
            self.set_status(400)
            for field in form.errors:
                r[field] = form.errors[field][0]
        self.finish(r)


class QuestionDetailHandler(BaseHandler):
    @authenticated
    async def get(self, question_id, *args, **kwargs):
        """获取一个问题的详细信息"""
        r = {}
        try:
            # get post and user info
            question = await self.application.objects.execute(
                Question.extend().where(Question.id == int(question_id))
            )
            if len(question) == 1:
                question = question[0]
                r = {
                    "user": question.user.to_json(),
                    "category": question.category,
                    "title": question.title,
                    "body": question.body,
                    "image": question.image_url,
                    "answer_num": question.answer_num,
                    # '%Y-%m-%d %H:%M:%S'
                    "created_time": question.created_time.strftime("%Y-%m-%d"),
                }
            else:
                self.set_status(404)
        except Question.DoesNotExist:
            self.set_status(404)
        self.finish(r)
