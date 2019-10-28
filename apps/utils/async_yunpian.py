#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
# yunpian doc: https://www.yunpian.com/doc/zh_CN/domestic/single_send.html
import json
from urllib.parse import urlencode
from tornado import httpclient
from tornado.httpclient import HTTPRequest
from mxforum.settings import YUNPIAN_SIGNATURE, YUNPIAN_APIKEY


class AsyncYunPian:
    def __init__(self):
        self.apikey = YUNPIAN_APIKEY

    async def send_single(self, code, mobile):
        "Send a single SMS"
        http_client = httpclient.AsyncHTTPClient()
        url = "https://sms.yunpian.com/v2/sms/single_send.json"
        text = "【{}】您的验证码是{}。如非本人操作，请忽略本短信".format(YUNPIAN_SIGNATURE, code)
        post_request = HTTPRequest(
            method="POST",
            url=url,
            body=urlencode(
                {"apikey": self.apikey, "mobile": str(mobile), "text": text}
            ),
        )
        res = await http_client.fetch(post_request)
        # print(res.body.decode("utf8"))
        return json.loads(res.body.decode("utf-8"))


if __name__ == "__main__":
    from functools import partial
    import tornado
    from mxforum.settings import YUNPIAN_APIKEY

    io_loop = tornado.ioloop.IOLoop.current()

    yunpian = AsyncYunPian(YUNPIAN_APIKEY)
    # run_sync 方法在运行完某个协程之后停止事件循环
    send_single_wrapper = partial(yunpian.send_single, "1234", "180180018000")
    io_loop.run_sync(yunpian, send_single)
