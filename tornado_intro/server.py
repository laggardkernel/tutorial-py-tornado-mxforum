#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et


import tornado.web
import tornado.ioloop
from tornado.options import define, options, parse_command_line

define("port", default=8000, help="run on the given port", type=int)
define("debug", default=True, help="enable debugger or not", type=bool)
options.parse_command_line()


class MainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write("hello world")


class PeopleIdHandler(tornado.web.RequestHandler):
    def initialize(self, name):
        self.db_name = name

    async def get(self, id, *arg, **kwargs):
        self.redirect(self.reverse_url("people_name", "toby"))


class PeopleNameHandler(tornado.web.RequestHandler):
    async def get(self, name, *arg, **kwargs):
        self.write("User name: {}".format(name))


class PeopleInfoHandler(tornado.web.RequestHandler):
    async def get(self, name, age, gender, *arg, **kwargs):
        self.write("User name: {}, age {}, gender {}".format(name, age, gender))


people_db = {"name": "toby"}
urls = [
    tornado.web.URLSpec(r"/", MainHandler, name="index"),
    tornado.web.URLSpec(
        r"/people/(\d+)/?", PeopleIdHandler, people_db, name="people_id"
    ),
    tornado.web.URLSpec(r"/people/(\w+)/?", PeopleNameHandler, name="people_name"),
    tornado.web.URLSpec(
        "/people/(?P<name>\w+)/(?P<id>\d+)/(?P<gender>\w+)/?",
        PeopleInfoHandler,
        name="people_info",
    ),
]

if __name__ == "__main__":
    app = tornado.web.Application(urls, debug=True)
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
