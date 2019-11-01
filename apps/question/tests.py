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


def test_add_question():
    token = generate_token()
    files = {"image": open(os.path.join(settings["media_root"], "test.jpg"), "rb")}
    data = {"title": "提问测试", "body": "此问题仅做测试，请勿回复", "category": "技术问答"}
    r = requests.post(
        "{}/questions/".format(HOST),
        headers={"tsessionid": token},
        data=data,
        files=files,
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_list_question():
    data = generate_token()
    r = requests.get("{}/questions/".format(HOST), headers={"tsessionid": data})
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_get_question(question_id):
    token = generate_token()
    r = requests.get(
        "{}/questions/{}/".format(HOST, question_id), headers={"tsessionid": token}
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_add_question_answers(question_id):
    token = generate_token()
    data = {"body": "这是一个问题的回答"}
    r = requests.post(
        "{}/questions/{}/answers/".format(HOST, question_id),
        headers={"tsessionid": token},
        json=data,
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_get_answers(question_id):
    token = generate_token()
    r = requests.get(
        "{}/questions/{}/answers/".format(HOST, question_id),
        headers={"tsessionid": token},
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_add_answer_reply(id_):
    token = generate_token()
    data = {"replied": 1, "body": "楼中楼回复测试"}
    r = requests.post(
        "{}/answers/{}/replies/".format(HOST, id_),
        headers={"tsessionid": token},
        json=data,
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


def test_get_answer_replies(id_):
    token = generate_token()
    r = requests.get(
        "{}/answers/{}/replies/".format(HOST, id_), headers={"tsessionid": token}
    )
    print(r.status_code)
    print(json.dumps(r.json(), ensure_ascii=False, indent=4))


if __name__ == "__main__":
    # test_authenticated()
    # test_add_question()
    # test_list_question()
    # test_get_question(1)
    # test_add_question_answers(1)
    # test_get_answers(1)
    # test_add_answer_reply(1)
    test_get_answer_replies(1)
