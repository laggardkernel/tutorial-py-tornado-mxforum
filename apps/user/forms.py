#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Regexp


# https://www.jianshu.com/p/5fbb85967bfd
MOBILE_REGEX = "^(13[0-9]|14[5-9]|15[0-3,5-9]|16[2,5,6,7]|17[0-8]|18[0-9]|19[1,3,5,8,9])\\d{8}$"


class SmsCodeForm(Form):
    mobile = StringField(
        "手机号码",
        validators=[
            DataRequired(message="请输入手机号码"),
            Regexp(MOBILE_REGEX, message="请输入合法的手机号码"),
        ],
    )
