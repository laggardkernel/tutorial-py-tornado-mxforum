#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import json
import requests

web_url = "http://127.0.0.1:8888"


def test_sms():
    url = "{}/code/".format(web_url)
    data = {"mobile": "18018001800"}
    res = requests.post(url, json=data)
    print(json.loads(res.text))


if __name__ == "__main__":
    test_sms()
