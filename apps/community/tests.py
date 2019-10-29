#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import os
from datetime import datetime
from time import time
import requests
import jwt

from mxforum.settings import settings

HOST = "http://127.0.0.1:8888"


def generate_token():
    current_time = time()
    data = jwt.encode(
        {"name": "dummy", "id": 1, "exp": current_time + 60 * 10},
        settings["secret_key"],
    ).decode("utf-8")
    print("input data: {}".format(data))
    return data


def test_authenticated():
    data = generate_token()
    r = requests.get("{}/groups/".format(HOST), headers={"tsessionid": data})


def test_community_creation():
    token = generate_token()
    files = {
        "front_image": open(os.path.join(settings["media_root"], "test.jpg"), "rb")
    }
    data = {
        "name": "学前教育交流角",
        "desc": "这里是学前教育交流中心，欢迎各位一起交流讨论。",
        "notice": "禁膜",
        "category": "教育同盟",
    }
    r = requests.post(
        "{}/groups/".format(HOST), headers={"tsessionid": token}, data=data, files=files
    )
    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    # test_authenticated()
    test_community_creation()
