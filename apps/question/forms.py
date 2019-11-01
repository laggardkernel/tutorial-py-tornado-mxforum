#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from wtforms_tornado import Form
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, AnyOf


QUESTION_CATEGORIES = ["技术问答", "技术分享"]


class QuestionForm(Form):
    category = StringField("类别", validators=[AnyOf(values=QUESTION_CATEGORIES)])
    title = StringField(
        "标题", validators=[DataRequired("请输入标题"), Length(max=256, message="标题长度不得超过256")]
    )
    body = TextAreaField("内容", validators=[DataRequired(message="请输入内容")])


class AnswerForm(Form):
    body = StringField(
        "内容",
        validators=[DataRequired("请输入回答内容"), Length(max=1024, message="回答长度不能超过1024")],
    )

class AnswerReplyForm(Form):
    # 被回复者ID
    replied = IntegerField("被回复者", validators=[DataRequired("请输入您要回复的用户")])
    body = StringField(
        "内容",
        validators=[
            DataRequired("请输入评论内容"),
            Length(max=1024, message="评论内容长度不能大于1024"),
        ],
    )

