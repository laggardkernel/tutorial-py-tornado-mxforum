#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from mxforum.settings import YUNPIAN_SIGNATURE
import requests


class YunPian:
    def __init__(self, apikey):
        self.apikey = apikey

    def send_single(self, code, mobile):
        "Send a single SMS"
        # depends on Requests
        url = "https://sms.yunpian.com/v2/sms/single_send.json"
        text = "【{}】您的验证码是{}。如非本人操作，请忽略本短信".format(YUNPIAN_SIGNATURE, code)
        res = requests.post(
            url, data={"apikey": self.apikey, "mobile": str(mobile), "text": text}
        )
        return res


if __name__ == "__main__":
    from mxforum.settings import YUNPIAN_APIKEY

    yunpian = YunPian(YUNPIAN_APIKEY)
    res = yunpian.send_single(1234, "18000000001")
    print(res.text)
