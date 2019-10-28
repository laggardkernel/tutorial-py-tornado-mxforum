#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import json
from string import digits
from random import choice
from tornado.web import RequestHandler
from apps.user.forms import SmsCodeForm, RegisterForm
from apps.user.models import User
from apps.utils.async_yunpian import AsyncYunPian
from mxforum.handlers import RedisHandler


class RegisterHandler(RedisHandler):
    async def post(self, *args, **kwargs):
        r_data = {}
        params = self.request.body.decode("utf-8")
        params = json.loads(params)
        form = RegisterForm.from_json(params)
        if form.validate():
            mobile = form.mobile.data
            code = form.code.data
            password = form.password.data
            # check if the register code is valid
            redis_key = "{}_{}".format(mobile, code)
            # redis 内存存储，没太多必要使用异步查询。当然也可以使用 aioredis
            if not self.redis_conn.get(redis_key):
                self.set_status(400)
                r_data["code"] = "验证码错误或者失效"
            else:
                try:
                    # if the mobile number has been used
                    user = await self.application.objects.get(User, mobile=mobile)
                    self.set_status(400)
                    r_data["mobile"] = "用户已经存在"
                except User.DoesNotExist as e:
                    user = await self.application.objects.create(
                        User, mobile=mobile, password=password
                    )
                    r_data["id"] = user.id
        else:
            self.set_status(400)
            for field in form.errors:
                r_data[field] = form.errors[field][0]
        self.finish(r_data)


class SmsHandler(RedisHandler):
    def generate_code(self):
        """生成随机4位数字验证码"""
        random_str = []
        for i in range(4):
            random_str.append(choice(digits))
        return "".join(random_str)

    async def post(self, *args, **kwargs):
        # TODO: check existence of mobile number before registration
        r_data = {}
        params = self.request.body.decode("utf-8")
        # load and validate the mobile number with WTForm
        params = json.loads(params)
        sms_form = SmsCodeForm.from_json(params)
        if sms_form.validate():
            self.settings["debug"]
            code = self.generate_code()
            mobile = sms_form.mobile.data

            if self.application.settings["debug"]:
                print(mobile, code)
                r_json = {"code": 0}
            else:
                # https://www.yunpian.com/doc/zh_CN/domestic/single_send.html
                yunpian = AsyncYunPian()
                r_json = await yunpian.send_single(code, mobile)

            if r_json["code"] != 0:
                self.set_status(400)
                r_data["mobile"] = r_json["msg"]
            else:
                print(mobile, code)
                # write validation code into Redis
                self.redis_conn.set("{}_{}".format(mobile, code), 1, ex=10 * 60)
        else:
            self.set_status(400)
            for field in sms_form.errors:
                r_data[field] = sms_form.errors[field][0]
        self.finish(r_data)
