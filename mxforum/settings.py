#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

import os
from dotenv import load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

YUNPIAN_APIKEY = os.environ.get("YUNPIAN_APIKEY", None)
YUNPIAN_SIGNATURE = os.environ.get("YUNPIAN_SIGNATURE", None)

settings = {
    "static_search": BASE_DIR,
    "static_url_prefix": "/static",
    "template_path": "templates",
    "db": {
        "host": "127.0.0.1",
        "user": "root",
        "password": "root",
        "name": "message",
        "port": 3306,
    },
    "redis": {"host": "127.0.0.1"},
}
