#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
from apps.user.models import User
from apps.community.models import Group, GroupMember, Post, Comment, CommentLike

# Note: the database object is async
from mxforum.settings import database


def init():
    # create tables
    database.create_tables([User])
    database.create_tables([Group, GroupMember])
    database.create_tables([Post, Comment, CommentLike])


if __name__ == "__main__":
    init()
