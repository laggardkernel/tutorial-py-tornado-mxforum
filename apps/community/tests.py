#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import os
from datetime import datetime
from time import time
import json
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


def test_group_creation():
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


def test_group_list():
    data = generate_token()
    r = requests.get("{}/groups/".format(HOST), headers={"tsessionid": data})
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_apply_group(group_id, apply_reason):
    token = generate_token()
    data = {"apply_reason": apply_reason}
    r = requests.post(
        "{}/groups/{}/members/".format(HOST, group_id),
        headers={"tsessionid": token},
        json=data,
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_get_group(group_id):
    token = generate_token()
    r = requests.get(
        "{}/groups/{}/".format(HOST, group_id), headers={"tsessionid": token}
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_add_post(group_id):
    token = generate_token()
    data = {"title": "Tornado 从入门到实战", "body": "Tornado 从入门到实战"}
    r = requests.post(
        "{}/groups/{}/posts/".format(HOST, group_id),
        headers={"tsessionid": token},
        json=data,
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_get_post(post_id):
    token = generate_token()
    r = requests.get(
        "{}/posts/{}/".format(HOST, post_id), headers={"tsessionid": token}
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_add_post_comment(post_id):
    token = generate_token()
    data = {"body": "我们的未来是星辰大海"}
    r = requests.post(
        "{}/posts/{}/comments/".format(HOST, post_id),
        headers={"tsessionid": token},
        json=data,
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_get_comments(post_id):
    token = generate_token()
    r = requests.get(
        "{}/posts/{}/comments/".format(HOST, post_id), headers={"tsessionid": token}
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_add_comment_reply(comment_id):
    token = generate_token()
    data = {"replied": 1, "body": "楼中楼回复测试"}
    r = requests.post(
        "{}/comments/{}/replies/".format(HOST, comment_id),
        headers={"tsessionid": token},
        json=data,
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_get_comment_replies(comment_id):
    token = generate_token()
    r = requests.get(
        "{}/comments/{}/replies/".format(HOST, comment_id),
        headers={"tsessionid": token},
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))

def test_add_comment_like(comment_id):
    token = generate_token()
    r = requests.post(
        "{}/comments/{}/likes/".format(HOST, comment_id),
        headers={"tsessionid": token},
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))

if __name__ == "__main__":
    # test_authenticated()
    # test_group_creation()
    # test_group_list()
    # test_apply_group(1, "test")
    # test_get_group(1)
    # test_add_post(1)
    # test_get_post(1)
    # test_add_post_comment(1)
    # test_get_comments(1)
    # test_add_comment_reply(2)
    # test_get_comment_replies(2)
    test_add_comment_like(2)
