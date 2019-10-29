#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Regexp, Length


# https://www.jianshu.com/p/5fbb85967bfd
MOBILE_REGEX = (
    "^(13[0-9]|14[5-9]|15[0-3,5-9]|16[2,5,6,7]|17[0-8]|18[0-9]|19[1,3,5,8,9])\\d{8}$"
)


class SmsCodeForm(Form):
    mobile = StringField(
        "手机号码",
        validators=[
            DataRequired(message="请输入手机号码"),
            Regexp(MOBILE_REGEX, message="请输入合法的手机号码"),
        ],
    )


class LoginForm(Form):
    mobile = StringField(
        "手机号码",
        validators=[
            DataRequired(message="请输入手机号码"),
            Regexp(MOBILE_REGEX, message="请输入合法的手机号码"),
        ],
    )
    password = StringField(
        "密码", validators=[DataRequired(message="请输入密码"), Length(8, message="密码最短为8位")]
    )


class RegisterForm(Form):
    mobile = StringField(
        "手机号码",
        validators=[
            DataRequired(message="请输入手机号码"),
            Regexp(MOBILE_REGEX, message="请输入合法的手机号码"),
        ],
    )
    # 验证码 Redis 查询需要异步，不在这里实现
    code = StringField(
        "验证码",
        validators=[DataRequired(message="请输入验证码"), Length(4, 4, message="请确定验证码位数为4")],
    )
    password = StringField(
        "密码", validators=[DataRequired(message="请输入密码"), Length(8, message="密码最短为8位")]
    )
