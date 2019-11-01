#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import json
from tornado.web import RequestHandler
from playhouse.shortcuts import model_to_dict

from mxforum.handlers import BaseHandler
from apps.utils.decorators import authenticated
from apps.utils.serializers import datetime2json
from apps.user.models import User
from apps.community.models import Group, GroupMember, Post, Comment, CommentLike
from apps.community.forms import (
    GroupForm,
    GroupApplyForm,
    PostForm,
    PostCommentForm,
    CommentReplyForm,
)


class GroupHandler(BaseHandler):
    async def get(self, *args, **kwargs):
        # 获取小组列表
        r = []
        # extend() is a custom method to do a join query with User
        query = Group.extend()

        # 根据组/社区类别做过滤
        category = self.get_argument("c", None)  # c for category
        if category:
            query = query.filter(Group.category == category)

        # 根据参数进行排序
        order = self.get_argument("o", "new")  # o for order
        if order and order == "hot":
            query = query.order_by(Group.member_num.desc())
        elif order == "new":
            query = query.order_by(Group.created_time.desc())
        limit = self.get_argument("limit", None)
        if limit:
            query = query.limit(int(limit))
        groups = await self.application.objects.execute(query)
        for group in groups:
            group_dict = model_to_dict(group)
            group_dict["front_image"] = group.front_image_url
            r.append(group_dict)

        self.finish(json.dumps(r, default=datetime2json))

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
                    break
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
                self.set_status(201)
        else:
            self.set_status(400)
            for field in form.errors:
                r[field] = form.errors[field][0]
        self.finish(r)


class GroupMemberHandler(BaseHandler):
    @authenticated
    async def post(self, group_id, *args, **kwargs):
        """申请加入小组"""
        r = {}
        params = self.request.body.decode("utf-8")
        params = json.loads(params)
        form = GroupApplyForm.from_json(params)
        if form.validate():
            try:
                group = await self.application.objects.get(Group, id=int(group_id))
                existed = await self.application.objects.get(
                    GroupMember, group=group, user=self.current_user
                )
                self.set_status(400)
                r["non_fields"] = "用户已经申请过"
            except Group.DoesNotExist:
                self.set_status(404)
            except GroupMember.DoesNotExist:
                group_member = await self.application.objects.create(
                    GroupMember,
                    group=group,
                    user=self.current_user,
                    apply_reason=form.apply_reason.data,
                )
                r["id"] = group_member.id
                self.set_status(201)
        else:
            self.set_status(400)
            for field in form.errors:
                r[field] = form.errors[field][0]
        self.finish(r)


class GroupDetaiHandler(BaseHandler):
    @authenticated
    async def get(self, group_id, *args, **kwargs):
        """获取小组基本信息"""
        r = {}
        try:
            group = await self.application.objects.get(Group, id=int(group_id))
            item = {}
            item["id"] = group.id
            item["name"] = group.name
            item["desc"] = group.desc
            item["notice"] = group.notice
            item["member_num"] = group.member_num
            item["post_num"] = group.post_num
            item["front_image"] = group.front_image_url
            r = item
        except Group.DoesNotExist:
            self.set_status(404)
        self.finish(r)


class PostHandler(BaseHandler):
    @authenticated
    async def get(self, group_id, *args, **kwargs):
        """获取小组内帖子"""
        r = []
        try:
            group = await self.application.objects.get(Group, id=int(group_id))
            group_member = await self.application.objects.get(
                GroupMember, group=group, user=self.current_user, status="agreed"
            )
            query = Post.extend()

            category = self.get_argument("category", None)
            if category == "hot":
                query = query.filter(Post.is_hot == True)
            elif category == "excellent":
                query = query.filter(Post.is_excellent == True)
            posts = await self.application.objects.execute(query)

            for post in posts:
                item = {
                    "user": {
                        "id": post.user.id,
                        "nickname": post.user.nickname or post.user.mobile,
                    },
                    "id": post.id,
                    "title": post.title,
                    "body": post.body,
                    "comment_num": post.comment_num,
                }
                r.append(item)
        except Group.DoesNotExist:
            self.set_status(404)
        except GroupMember.DoesNotExist:
            self.set_status(403)
        self.finish(json.dumps(r))

    @authenticated
    async def post(self, group_id, *args, **kwargs):
        """小组内发帖"""
        r = {}
        try:
            group = await self.application.objects.get(Group, id=int(group_id))
            group_member = await self.application.objects.get(
                GroupMember, group=group, user=self.current_user, status="agreed"
            )
            params = self.request.body.decode("utf-8")
            params = json.loads(params)
            form = PostForm.from_json(params)
            if form.validate():
                post = await self.application.objects.create(
                    Post,
                    user=self.current_user,
                    title=form.title.data,
                    body=form.body.data,
                    group=group,
                )
                group.post_num += 1
                await self.application.objects.update(group, only=["post_num"])
                r["id"] = post.id
                self.set_status(201)
            else:
                self.set_status(400)
                for field in form.errors:
                    r[field] = form.errors[field][0]
        except Group.DoesNotExist:
            self.set_status(404)
        except GroupMember.DoesNotExist:
            self.set_status(403)
        self.finish(r)


class PostDetailHandler(BaseHandler):
    @authenticated
    async def get(self, post_id, *args, **kwargs):
        """获取一个帖子的详细信息"""
        r = {}
        try:
            # get post and user info
            post = await self.application.objects.execute(
                Post.extend().where(Post.id == int(post_id))
            )
            if len(post) == 1:
                post = post[0]
                r = {
                    "user": post.user.to_json(),
                    "title": post.title,
                    "body": post.body,
                    "comment_num": post.comment_num,
                    # '%Y-%m-%d %H:%M:%S'
                    "created_time": post.created_time.strftime("%Y-%m-%d"),
                }
            else:
                self.set_status(404)
        except Post.DoesNotExist:
            self.set_status(404)
        self.finish(r)


class PostCommentHandler(BaseHandler):
    @authenticated
    async def get(self, post_id, *args, **kwargs):
        """Get all comments under a post"""
        r = []
        try:
            post = await self.application.objects.get(Post, id=int(post_id))
            comments = await self.application.objects.execute(
                Comment.extend()
                .where(Comment.post_id == int(post_id), Comment.commented.is_null(True))
                .order_by(Comment.created_time.desc())
            )
            for comment in comments:
                is_liked = False
                try:
                    comment_like = await self.application.objects.get(
                        CommentLike, comment_id=comment.id, user_id=self.current_user.id
                    )
                    is_liked = True
                except CommentLike.DoesNotExist:
                    pass
                comment_dict = {
                    "id": comment.id,
                    # User.created_time is not queried
                    "user": comment.user.to_json(),
                    "body": comment.body,
                    "reply_num": comment.reply_num,
                    "like_num": comment.like_num,
                    "is_liked": is_liked,
                }
                r.append(comment_dict)
        except Post.DoesNotExist:
            self.set_status(404)
        self.finish(json.dumps(r, default=datetime2json))

    @authenticated
    async def post(self, post_id, *args, **kwargs):
        """新增评论"""
        r = {}
        try:
            post = await self.application.objects.get(Post, id=int(post_id))
            params = self.request.body.decode("utf-8")
            params = json.loads(params)
            form = PostCommentForm.from_json(params)
            if form.validate():
                comment = await self.application.objects.create(
                    Comment, user=self.current_user, post=post, body=form.body.data
                )
                post.comment_num += 1
                await self.application.objects.update(post, only=["comment_num"])
                r["id"] = comment.id
                r["user"] = {
                    "id": self.current_user.id,
                    "nickname": self.current_user.nickname or self.current_user.mobile,
                }
                self.set_status(201)
            else:
                self.set_status(400)
                for field in form.errors:
                    r[field] = form.errors[field][0]
        except Post.DoesNotExist:
            self.set_status(404)
        self.finish(r)


class CommentReplyHandler(BaseHandler):
    @authenticated
    async def get(self, comment_id, *args, **kwargs):
        r = []
        try:
            comment = await self.application.objects.get(Comment, id=int(comment_id))
            replies = await self.application.objects.execute(
                Comment.extend()
                .where(Comment.commented_id == int(comment_id))
                .order_by(Comment.created_time)
            )
            for reply in replies:
                # is_liked = False
                # try:
                #     comment_like = await self.application.objects.get(
                #         CommentLike, comment_id=comment.id, user_id=self.current_user.id
                #     )
                #     is_liked = True
                # except CommentLike.DoesNotExist:
                #     pass
                reply_dict = {
                    "id": reply.id,
                    # User.created_time is not queried
                    "user": reply.user.to_json(),
                    "body": reply.body,
                    "reply_num": reply.reply_num,
                    # "like_num": reply.like_num,
                    # "is_liked": is_liked,
                    "created_time": reply.created_time.strftime("%Y-%m-%d"),
                }
                r.append(reply_dict)
        except Comment.DoesNotExist:
            self.set_status(404)
        self.finish(json.dumps(r, default=datetime2json))

    @authenticated
    async def post(self, comment_id, *args, **kwargs):
        r = {}
        try:
            comment = await self.application.objects.get(Comment, id=int(comment_id))
            params = self.request.body.decode("utf-8")
            params = json.loads(params)
            form = CommentReplyForm.from_json(params)
            if form.validate():
                replied = await self.application.objects.get(User, id=form.replied.data)

                reply = await self.application.objects.create(
                    Comment,
                    user=self.current_user,
                    commented=comment,
                    replied=replied,
                    body=form.body.data,
                )

                comment.reply_num += 1
                await self.application.objects.update(comment, only=["reply_num"])

                r["id"] = reply.id
                r["user"] = {
                    "id": self.current_user.id,
                    "nickname": self.current_user.nickname or self.current_user.mobile,
                }
                self.set_status(201)
            else:
                self.set_status(400)
                for field in form.errors:
                    r[field] = form.errors[field][0]
        except Comment.DoesNotExist:
            self.set_status(404)
        except User.DoseNotExist:
            self.set_status(400)
            r["replied"] = "被回复者不存在"
        self.finish(r)


class CommentLikeHandler(BaseHandler):
    @authenticated
    async def post(self, comment_id, *args, **kwargs):
        r = {}
        try:
            comment = await self.application.objects.get(Comment, id=int(comment_id))
            like = await self.application.objects.get(
                CommentLike, user=self.current_user, comment_id=int(comment_id)
            )
            if like:
                r["error"] = "已经赞过，请勿重复点赞"
                self.set_status(400)

        except Comment.DoesNotExist:
            self.set_status(404)
        except CommentLike.DoesNotExsit:
            # NOTE: 暂时对自己赞自己不做限制
            like = await self.application.objects.create(
                CommentLike, user=self.current_user, comment=comment
            )

            comment.like_num += 1
            await self.application.objects.update(comment, only=["like_num"])

            r["id"] = like.id
            self.set_status(201)

        self.finish(r)
