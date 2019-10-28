#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import os
import tornado.ioloop
import tornado.web
from mxforum.urls import urlpatterns
from mxforum.settings import settings

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

if __name__ == "__main__":
    # 集成 json 到 WTForms
    import wtforms_json

    wtforms_json.init()
    app = tornado.web.Application(urlpatterns, debug=True, **settings)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
