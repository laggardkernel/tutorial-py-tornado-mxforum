#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import os
import tornado.ioloop
import tornado.web
from peewee_async import Manager
from mxforum.urls import urlpatterns
from mxforum.settings import settings, database
from tornado.options import define, options

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
define("port", default=8888, help="run on the given port ", type=int)

if __name__ == "__main__":
    tornado.options.parse_command_line()

    # 集成 json 到 WTForms
    import wtforms_json

    wtforms_json.init()
    app = tornado.web.Application(urlpatterns, **settings)
    app.listen(options.port)

    # create async db manager
    objects = Manager(database)
    # disable sync query in MySQL
    database.set_allow_sync(False)

    app.objects = objects
    tornado.ioloop.IOLoop.current().start()
