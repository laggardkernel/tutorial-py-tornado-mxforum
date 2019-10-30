#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from wtforms_tornado import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, AnyOf


GROUP_CATEGORIES = ["教育同盟", "同城交易", "程序设计", "生活兴趣"]


class GroupForm(Form):
    name = StringField(
        "名称", validators=[DataRequired(message="请输入小组名称"), Length(max=100)]
    )
    category = StringField("类别", validators=[AnyOf(values=GROUP_CATEGORIES)])
    desc = TextAreaField("简介", validators=[DataRequired(message="请输入简介")])
    notice = TextAreaField("公告", validators=[DataRequired(message="请输入公告")])


class GroupApplyForm(Form):
    apply_reason = StringField("申请理由", validators=[DataRequired(message="请输入申请理由")])


class PostForm(Form):
    title = StringField("标题", validators=[DataRequired("请输入标题")])
    body = StringField("内容", validators=[DataRequired("请输入内容")])


class PostCommentForm(Form):
    body = StringField(
        "内容",
        validators=[
            DataRequired("请输入评论内容"),
            Length(max=1000, message="评论内容长度不能大于1000"),
        ],
    )
