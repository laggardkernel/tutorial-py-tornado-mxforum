#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

import os
from dotenv import load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

YUNPIAN_APIKEY = os.environ.get("YUNPIAN_APIKEY", None)
