#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import functools
import jwt
from apps.user.models import User


def authenticated(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        # JWT is passed from Header in our site as "tsessionid" (custom name)
        tsessionid = self.request.headers.get("tsessionid", None)
        if tsessionid:
            try:
                data = jwt.decode(
                    tsessionid,
                    self.application.settings["secret_key"],
                    leeway=1,
                    options={"verify_exp": True},
                )
                user_id = int(data["id"])
                # get user according to the user_id and set it to _current_user
                try:
                    user = await self.application.objects.get(User, id=user_id)
                    self._current_user = user

                    # 注意返回异步的装饰函数
                    await method(self, *args, **kwargs)
                except User.DoesNotExist as e:
                    self.set_status(401)
            except jwt.exceptions.ExpiredSignatureError as e:
                self.set_status(401)  # forbidden
        else:
            self.set_status(401)
        self.finish({})

    return wrapper
