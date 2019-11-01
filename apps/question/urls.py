#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from tornado.web import url
from apps.question.handlers import QuestionHandler, QuestionDetailHandler

urlpatterns = (
    url("/questions/", QuestionHandler),
    url("/questions/(\d+)/", QuestionDetailHandler),
)
