#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from tornado.web import url, StaticFileHandler
from mxforum.settings import settings
from apps.user import urls as user_urls
from apps.community import urls as community_urls

urlpatterns = [
    # 将用户上传数据与前端静态文件分离开来。
    (url("/media/(.*)", StaticFileHandler, {"path": settings["media_root"]}))
]


urlpatterns += user_urls.urlpatterns
urlpatterns += community_urls.urlpatterns
