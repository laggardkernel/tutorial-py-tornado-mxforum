#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from tornado.web import url
from apps.community.handlers import GroupHandler, GroupMemberHandler, GroupDetaiHandler, PostHandler

urlpatterns = (
    url("/groups/", GroupHandler),
    url("/groups/(\d+)/", GroupDetaiHandler),
    url("/groups/(\d+)/members/", GroupMemberHandler),
    url("/groups/(\d+)/posts/", PostHandler),
)
