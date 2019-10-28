#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from apps.user.models import User

# Note: the database object is async
from mxforum.settings import database


def init():
    # create tables
    database.create_tables([User])


if __name__ == "__main__":
    init()
