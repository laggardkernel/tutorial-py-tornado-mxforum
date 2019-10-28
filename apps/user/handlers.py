#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import json
from string import digits
from random import choice
from functools import partial
from tornado.web import RequestHandler
from apps.user.forms import SmsCodeForm
from apps.utils.async_yunpian import AsyncYunPian
from mxforum.settings import YUNPIAN_SIGNATURE, YUNPIAN_APIKEY
from mxforum.handlers import RedisHandler


class SmsHandler(RedisHandler):
    def generate_code(self):
        """生成随机4位数字验证码"""
        random_str = []
        for i in range(4):
            random_str.append(choice(digits))
        return "".join(random_str)

    async def post(self, *args, **kwargs):
        r_data = {}
        params = self.request.body.decode("utf-8")
        # validate params with WTForm
        params = json.loads(params)
        sms_form = SmsCodeForm.from_json(params)
        if sms_form.validate():
            code = self.generate_code()
            mobile = sms_form.mobile.data
            yunpian = AsyncYunPian()
            r_json = await yunpian.send_single(code, mobile)
            # https://www.yunpian.com/doc/zh_CN/domestic/single_send.html
            if r_json["code"] != 0:
                self.set_status(400)
                r_data["mobile"] = r_json["msg"]
            else:
                # write validation code into Redis
                self.redis_conn.set("{}_{}".format(mobile, code), 1, 10 * 60)
        else:
            self.set_status(400)
            for field in sms_form.errors:
                r_data[field] = sms_form.errors[field][0]
        self.finish(r_data)
