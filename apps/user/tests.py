#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import json
import requests
import redis
from mxforum.settings import TEST_MOBILE

web_url = "http://127.0.0.1:8888"


def test_sms():
    url = "{}/code/".format(web_url)
    data = {"mobile": TEST_MOBILE}
    res = requests.post(url, json=data)
    print(json.loads(res.text))


def test_register():
    url = "{}/register/".format(web_url)
    # TODO: query the code from redis server automatically
    data = {"mobile": TEST_MOBILE, "code": "5691", "password": "12345678"}
    res = requests.post(url, json=data)
    print(json.loads(res.text))


if __name__ == "__main__":
    # test_sms()
    test_register()
