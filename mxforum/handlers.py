#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
# Similar to views in django
from tornado.web import RequestHandler
import redis


class BaseHandler(RequestHandler):
    def set_default_headers(self) -> None:
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Max-Age", 1000)
        self.set_header("Content-Type", "application/json")
        self.set_header(
            "Access-Control-Allow-Methods", "OPTIONS, GET, POST, DELETE, PUT, PATCH"
        )
        # tsessionid 为自定义token存储位置，之后会使用
        self.set_header(
            "Access-Control-Allow-Headers",
            "Content-Type, tsessionid, Access-Control-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods",
        )

    def options(self, *args, **kwargs):
        pass


class RedisHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.redis_conn = redis.StrictRedis(**self.settings["redis"])
