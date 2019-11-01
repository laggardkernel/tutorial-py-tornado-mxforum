# Tornado打造高并发论坛

## 部署
- `deployments`
- `.env`
- ~~`apps/ueditor/{config.json,settings.py}`~~，仅配置前端 `ueditor.config.js` 服务地址

## Pre
TODO

- [ ] peewee 文档翻阅（主要了解一下各种查询等基本操作的使用）
- [ ] 阅读 peewee 源码（视频主建议，推迟）
- [ ] peewee-async 使用
- [ ] peewee 模型中默认 id（隐式创建）类型
- [ ] 类似于Flask中的 flask shell，自动加载某些模型、数据库到python shell
- [ ] 改写 `peewee_extra_fields.SimplePasswordField` 模仿 `werkzeug.security.generate_password_hash` 存储hash的同时存储算法和盐。
- [ ] peewee Manager 自动保存新建的数据?
- [ ] peewee_migrate, peewee-db-evolve 过于粗糙，有没有类似 Flask-Migrate（基于Alembic）的傻瓜数据库迁移工具。
- [ ] 重写 model_to_dict 或者是添加User类方法，在nickname为空时，使用mobile作为nickname返回为JSON数据
- [x] 业务逻辑：限制点赞数量

References

- [Awesome asyncio](https://github.com/timofurrer/awesome-asyncio)

Note

- 前端源码可能老旧，直接GitHub，[TornadoForum](https://github.com/vannesspeng/TornadoForum)
- 前端页面部分没有完成
- 测试用例不规范，没有使用UnitTest，没有为测试用例使用单独的数据库
- 缺少面向对象思想，即没有业务协作模型的方法
- 业务逻辑上略有不足，如自己可以赞自己且点赞数量没做限制。毕竟是教学，暂时不做深究

## 01 Intro
非阻塞、epoll。

针对高并发、长连接而生。

应用：知乎、facebook。

特定

- 也是web服务器（自带服务器）
- 包括了异步http客户端，AsyncHttpClient
- 非常小的web框架和核心
- 天然支持长连接
- 有利于理解asyncio

教程内容

- tornado web基础
    - 为什么不能使用同步io
    - tornado url配置
    - define, options, parse_command_line
    - RequestHandler
    - template 机制
    - UIModule
- 异步io并发编程原理
    - 同步、异步、阻塞、非阻塞
    - select, poll, epoll
    - socket非阻塞
    - 事件循环
    - 协程
- AsyncHttpClient
    - 并发爬虫
- 异步驱动：aiomysql, peewee-async
    - aiomysql异步留言板
    - peewee数据操作
    - peewee-async，基于协程的ORM
    - peewee自动生成数据表
- aiofiles, wtforms
    - aiofiles异步写入文件
    - wtforms表单验证
    - wtforms数据保存
    - wtforms生成html
- 实战项目
    - 继承ueditor
    - 装饰器，tornado authenticated
    - 异步io authenticated_async
    - model_to_dict 序列化
    - 异步发送短信
    - RESTFul

## 03 为什么要学习tornado
### 比较
[从django、flask、tornado的部署说起](http://www.imooc.com/article/24759)

底层IO处理机制

1. tornado、gevent、asyncio、aiohttp：底层使用的是事件循环+协程
2. django和flask： 传统的模型，阻塞io模型

Tornado从python 3.5开始使用asyncio。

![](https://image.slidesharecdn.com/pythondevops-130304181525-phpapp02/95/python-devops-your-own-heroku-35-638.jpg?cb=1363265575)

Nginx主要完成代理转发。

Django写异步

- 需要WSGI server支持
- 类似于celery，分布式异步编程，使用worker

tornado集成web服务器，不需要专门配置wsgi server。

twisted模型：基于回调，每个请求都被注册为一个异步函数。回调模型只需要一个线程，短板是一旦高CPU计算就会堵住线程。

prefork模型：每个slave都是一个wsgi app，一个wsgi app只能处理一个请求。

asyncio, tornado, gevent 模型：由于回调写法不容易读也容易出错，于是回调写法被改为同步写法。

- asyncio 实现了类似于go corountine写法
- aiohttp则提供了类似 go net/http 的 http 处理库

### tornado优势

（Django、Flask不具备）

- 异步web服务的整套方案
- 不只是框架，也是服务器
- 基于协程
- websocket长连接（web聊天、消息推送）

### Tornado如何做到高并发
- 异步非阻塞IO
- 基于epoll的事件循环
- 协程提高了代码的可读写（看起来像是同步，去除了回调）

### 对应Tornado的误解
- Tornado只是框架
- 使用tornado就是高并发（需要全部异步）
- 使用了大量的同步IO
- 只要将耗时的操作放到线程池中就可以高并发（线程池，也会受到影响）
- tornado多线程和协程的单线程冲突（不冲突）

### async/await 而是 coroutine
- 功能性虽然相同，但是 coroutine 只是过渡方案。
- yield, await 混合使用使得代码可维护性变差
- 生成器只做自己
- 原生协程比基于装饰器协程块
- async/await 更符合Python风格
- 原生携程返回 awatitable 对象，装饰器协程返回的是 future（后边会解释）

## 04 异步和非阻塞

### Tornado 基本
- web framework: `RequestHandler`
- HTTPServer, AsyncHttpClient
- async networking lib: `IOLoop`, `IOStream`
- coroutine library, `tornado.gen`. (replace it with `await`)

### 阻塞、非阻塞、同步、异步
作者有相关高级课程介绍Python异步编程。

概念

- CPU速度远高于IO速度
- IO包括网络访问、本地文件访问，使用替代产品替代request，urllib
- 网络IO大部分时间都是处于等待

阻塞、非阻塞

调用函数时，当前线程被挂起。

同步、异步：针对消息通信机制，获取结果的方式。

### Socket的非阻塞IO请求
request阻塞

- 三次TCP握手
- 等待服务器响应

request -> urllib -> socket

通过socket直接获取HTML。

socket直接使用非阻塞需要不断循环判断请求是否有返回值。

```python
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setblocking(False)
host='www.baidu.com'

try:
    client.connect((host,80))
except BlockingIOError as e:
    # 如何利用空闲时间：select, poll, epoll
    pass

# send, recv 都需要while True: try ... excpet ...
```

### select, poll, epoll
IO多路复用机制。

通过一种机制，一个进程可以监视多个描述符，一旦某个描述符就绪（可读就绪或者可写就绪），通知程序进行相应的读写操作。

select, poll, epoll 实质还是同步IO，它们都需要在读写事件后自己负责进行读写，读写过程阻塞。

TODO：比较select, poll, epoll.

### 事件循环
不断查询哪些事件就绪，然后调用回调函数处理。

### 协程
回调模式问题

- 回调过深后代码难以维护
- 栈撕裂造成异常无法向上抛出

协程，可以被暂停并切换到其他协程运行的函数。

### AsyncHttpClient
```python
if __name__ == '__main__':
    import tornado
    # 单例模式
    io_loop=tornado.ioloop.IOLoop.current()
    # run_sync 运行完某个协程后停止事件循环
    io_loop.run_sync(async_func)
    # or
    # async.get_event_loop().run_until_complete(async_func())

    # or run it forever
    import asyncio
    asyncio.ensure_future(async_func)
    asyncio.get_event_loop().run_forever()
```

### Tornado 实现异步爬虫
异步，只是应用于IO，CPU密集没必要使用。

基本就是参照文档在讲解。[Queue example - a concurrent web spider](http://www.tornadoweb.org/en/stable/guide/queues.html)

## 05 Tornado Web 基础
debug开启，自动重启，抛出详细异常到响应页面

在Tornado中不要使用同步IO。但方法内没有await没必要使用async。

### URL
URL规则定义使用正则表达式。

URL伪斜杠不会被Tornado自动处理，使用正则中`?`即可。

```
# 正则命名
(P<name>\w+)
```

### define, options
命令行解析参数

```python
from tornado.options import define, options, parse_command_line

define('port', default=8000, help="run on the given port",type=int)
options.parse_command_line()
```

`options` 为一个雷，全局只有一个 options 对象，不需要实例化。

使用格式为 `--port=8002` 不可用空格分隔。

`options.parse_config_file("default.conf")` 读取文件内配置。配置文件类似 ini 等于号赋值。

### RequestHandler
[RequestHandler 方法](http://www.tornadoweb.org/en/stable/web.html)

`initialize(self)` 初始化handler类的过程。

`prepare()` 请求之前。（如打印日志）

`on_finish()`，对应 prepare。（关闭句柄，清理内存）

获取参数

- query
    - `self.get_query_argument(key)`
    - `self.get_query_arguments()`
- `self.get_argument(key)` 不只针对请求参数，可以同时从查询参数和实体中获取
- `self.get_body_argument()`, `application/x-www-form-urlencoded`
- 所有参数：`self.request.arguments` 属性

获取json数据：

```python
import json
...
params=self.request.body.decode('utf-8')
data=json.loads(params)
```

自定义错误

```python
try:
    ...
except Exception as e:
    # 自定义错误码
    self.set_status(500)

# 自定义，覆盖错误返回函数
def write_error(self, status_code, **kwargs):
    pass
```

输出 `self.write()`, 此方法可以多次调用。写到缓存区后，一次输出。为长连接。

`self.finish()` 可以会写数据，同时关闭连接。字典被自动返回为 json 类型。

`self.redirect()`. `self.redirect("", permanent=True)`

### RequestHandler子类
`RedirectHandler` 默认永久重定向。

`self.redirect()` v.s. `RedirectHandler()`。前者主要用于请求方法中，默认临时；后者默认永久。

`StaticFileHandler`.

应用实例初始化时，设置 `static_path` 以及 `static_url_prefix`（默认 `/static`）。

### Template
`self.render()`

`self.render_string()`，需要 write 到客户端。

`template_path` 文件夹名称（相对于项目目录）。

django尽量较少在模板中写python代码，但是tornado则尽可能支持python。模板文件到底有前端还是后端来维护，如果过多的python代码支持，则需要后端对于前端更了解。

也就是说，django模板限制是为了分离前后端。

模板函数 `{{ static_url('css/public.css') }}`.

`static_url` 函数创建了一个基于文件内容的hash值，并将其添加到URL末尾（查询字符串的参数v）。这个hash值确保浏览器总是加载一个文件的最新版而不是之前的缓存版本。无论是在你应用的开发阶段，还是在部署到生产环境使用时，都非常有用，因为你的用户不必再为了看到你的静态内容而清除浏览器缓存了。

UIModule 类似于 Jinja2 中 macro。

```python
class OrderModule(tornado.web.UIModule):
    def calc_total(self, price, nums):
        return price*nums

    def render(self, order, *args, **kwargs):
        # pass func into template, and render it as string (类似于宏）
        return self.render_string('ui_modules/order_list.html', order=order, calc_total=self.calc_total)
```

### settings
[app configuration](http://www.tornadoweb.org/en/stable/web.html#application-configuration)

## 06 aiomysql完成留言板功能
aiomysql 基于 asyncio。asyncio支持的库，Tornado可以直接使用。

## 07 peewee 功能介绍
本章主要是peewee使用，读文档应该就可以知道基本使用。

ORM

- 隔离数据库差异
- 抽象数据库文Python对象

常见orm：django orm, sqlalchemy, peewee.

async-peewee 活跃度高。

peewee 外键名字自动加 `_id` 后缀。外键自动加索引。

```python
class Goods(BaseModel):
    supplier = ForeignKeyField(Supplier, verbose_name="商家", backref="goods")
    name = CharField(max_length=100, verbose_name="商品名称", index=True)
    click_num = IntegerField(default=0, verbose_name="点击数")
    goods_num = IntegerField(default=0, verbose_name="库存数")
    price = FloatField(default=0.0, verbose_name="价格")
    brief = TextField(verbose_name="商品简介")

    class Meta:
        table_name = "goods"
```

数据库最大值，即便数据库被清空也会记录之前的ID最大值。

`.select()`返回 `ModelSelect` 对象。迭代时会执行SQL查询，返回模型实例。

TODO: 阅读 peewee 源码。

`Goods.delete().where(Goods.price > 150).execute()` 为同步的。

```python
# update click_num=100 where id =1
Goods.update(click_num=Goods.click_num+1).where(Goods.id==1).execute()
```

删除数据

- `good.delete_instance()`
- `Goods.delete().where(Goods.price>150).execute()`

注意`try...except`捕捉错误避免操作失误。

Note:

- peewee 模型中 `null=False` 为默认值，也就是字段默认不允许为空

### peewee async usage
`peewee-async`, depends on `aiomysql` for MySQL database.

[peewee-async doc](https://peewee-async.readthedocs.io/en/latest/)

不能再使用 `Goods.save()` 阻塞式存储。而是通过新的管理器进行操作。

```python
database = peewee_async.MySQLDatabase(
    'message', host="127.0.0.1", port=3306, user="root", password="root"
)

objects = peewee_async.Manager(database)

# No need for sync anymore!


database.set_allow_sync(False)

async def handler():
    # await objects.create(Goods, supplier_id=7, name="53度水井坊臻酿八號500ml",
    #                      click_num=20, goods_num=1000, price=500, brief="州茅台酒厂（集团）保健酒业有限公司生产")
    goods = await objects.execute(Goods.select())
```

**Caveats**:

```
peewee-async==0.5.12
  - peewee [required: >=2.8.0,<=2.10.2, installed: 3.12.0]
```

peewee-async 0.6+ 开始仅支持 peewee 3.5+.

```
pipenv install peewee-async --pre
```

## 08 WTForms
略，已经学过了。

`tornado-forms` 库，解决实例化是直接传入请求中JSON参数问题。[tornado-wtform on GitHub](https://github.com/puentesarrin/wtforms-tornado) 仅仅是JSON参数问题，POST 的 formdata 可以正常处理。

```
TypeError: formdata should be a multidict-type wrapper that supports the "getlist" method
```

```python
import tornado.ioloop
import tornado.web

from wtforms.fields import IntegerField
from wtforms.validators import Required
from wtforms_tornado import Form

class SumForm(Form):

    a = IntegerField(validators=[Required()])
    b = IntegerField(validators=[Required()])

class SumHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

    def post(self):
        form = SumForm(self.request.arguments)
        if form.validate():
            self.write(str(form.data['a'] + form.data['b']))
        else:
            self.set_status(400)
            self.write("" % form.errors)

application = tornado.web.Application([
    (r"/", SumHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```

可以参考 tornado-wtform 源码，实际上是实现了一个类 `TornadoInputWrapper` 加入了` getlist` 方法。

```python
class TornadoInputWrapper(object):
    # ...
    def getlist(self, name):
        try:
            return [escape.to_unicode(v) for v in self._wrapped[name]]
        except KeyError:
            return []


class Form(form.Form):
    def __init__(self, formdata=None, obj=None, prefix='', locale_code='en_US',
             **kwargs):
        self._locale_code = locale_code
        super(Form, self).__init__(formdata, obj, prefix, **kwargs)

    def process(self, formdata=None, obj=None, **kwargs):
        if formdata is not None and not hasattr(formdata, 'getlist'):
            formdata = TornadoInputWrapper(formdata)
        super(Form, self).process(formdata, obj, **kwargs)
```

主键要设置自动递增，否则默认为0，第2次会冲突。

渲染时要注意关闭默认的转义。

```html
    {% autoescape None %}
    {% for field in message_form %}
        <span>{{ field.label.text }} :</span>
        {{ field(placeholder="请输入"+field.label.text) }}

        {% if field.errors %}
            {% for error_msg in field.errors %}
                <div class="error-msg">{{ error_msg }}</div>
            {% end %}
            {% else %}
                <div class="error-msg"></div>
        {% end %}
    {% end %}
```

## 09 RESTFul API、需求分析和代码结构设计
### 前后端分离
为何前后端分离

- pc, 移动端，多端试用
- SPA开发模式（单页面）流行
- 前后端端开发职责不清（模板语言由谁来写）
- 开发效率，前后端互相等待（使用RESTFul只要大家规划好API就可以开始干活）
- 前端一致配合着后端，能力受限
- 后端开发语言和模板语言高度耦合

Django 限制语法，但是 Mako 却没有限制。

前后端分离缺点

- 前后端学习门槛增加（如前端需要填充数据到页面）
- 数据依赖导致**文档**重要性增加（解释API）
- 前端工作量增加
- SEO难度加大
- 后端开发模式迁移增加了成本

### RESTFul API
表现层状态转移架构(Representational State Transfer, REST)

+ 客户端-服务端，二者有明确界限；
+ 无状态，客户端请求包含所有必要信息，服务器不能在两次响应之间保存客户端任何状态。易伸缩；
+ 缓存，可将服务器响应标记为可缓存和不可缓存；
+ 接口统一，协议必须一致，常用统一接口HTTP；
+ 系统分层，客户端与服务器之间可以按需插入代理服务器、缓存或网关；
+ 按需代码，可选从服务器上下载代码，在客户端环境中执行；

（个人理解，基于HTTP协议，是将HTTP动作将资源操作相互绑定。同时也是前后端分离的一种标准。）

> 客户端与服务器之间，传递这种资源的某种表现层。
>
> 比如，文本可以用txt格式表现，也可以用HTML格式、XML格式、JSON格式表现，甚至可以采用二进制格式；图片可以用JPG格式表现，也可以用PNG格式表现。

- 轻量，直接通过HTTP，不需要额外协议
- 面向资源，URL是一个资源。（通过HTTP方法操作资源）
- 数据描述简单，JSON或者XML

参考

- [理解RESTful架构](https://www.ruanyifeng.com/blog/2011/09/restful.html)
- [RESTful API 设计指南](http://www.ruanyifeng.com/blog/2014/05/restful_api.html)

### 需求分析
开发前分析。

社区小组

- 小组创建，加入小组。
- 小组中发帖、评论。
- 评论下回复
- 评论点赞

问答

- 发布提问，问答分类
- 回答提问

个人中心

- 个人信息修改
- 消息管理

### 代码结构设计
根据Flask，或者模仿Django模板。

```
.
├── apps/
│   ├── community/
│   │   ├── __init__.py
│   │   ├── handler.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── urls.py
│   ├── question/
│   │   └── __init__.py
│   ├── user/
│   │   └── __init__.py
│   ├── utils/
│   │   └── __init__.py
│   └── __init__.py
├── media/ # 上传的文件
├── mxforum/
│   ├── __init__.py
│   ├── handler.py # 视图函数
│   └── settings.py
├── requirements/
├── static/
│   ├── css/
│   ├── img/
│   └── js/
├── templates/
├── tools/
│   └── __init__.py
├── Pipfile
├── Pipfile.lock
├── README.md
└── server.py # 开始程序
```

## 10 用户登录和注册
### RESTFul API 格式规范
返回json

HTTP 状态码决定请求状态，而不是根据数据本身，数据本身可选作为详细说明。

```
{

}
```

### 验证码
保存验证码

- 保存到缓存
- 数据库中
- Redis缓存服务器（推荐）
    - Redis失效时间
    - 速度快于保存到数据库中

云片网发送短信验证码。调用[云片国内短信API](https://www.yunpian.com/doc/zh_CN/domestic/list.html)。

text 为经过审核的短信模板（模板必须经过服务商审核，以免被用来发送垃圾短信）


### tornado 集成短信发送
开发过程中尽量使用 debug 模式运行。

#### wtforms-json
pitfall: `Form(param)` 中若参数为字符串（可迭代对象），只有第一个字符被输入。

`self.request.arguments` 字典中每个键对应的值为list，为什么？Tornado自动处理用户请求的数据。而用户提交数据时，每个键的值就是一个字符串。

[`wtforms-json`](https://github.com/kvesteri/wtforms-json)

[wtforms-json doc](https://wtforms-json.readthedocs.io/en/latest/)

> Adds smart json support for WTForms. Useful for when using WTForms with RESTful APIs.

- Adds support for booleans (WTForms doesn’t know how to handle False boolean values)
- Adds support for None type FormField values
- Adds support for None type Field values
- Support for patch data requests with patch_data Form property
- Function for **converting JSON data into dict that WTForms understands** (`flatten_json()` function)

`Form.from_json()` 此属性为 monkeypatch。

#### redis 存储验证码
[redis-py](https://github.com/andymccurdy/redis-py)

## 登录
### 找回peewee中passwordfield
为什么？自己封装一下hash函数不可以吗？

别用他的方案，参考 [juancarlospaco/peewee-extra-fields](https://github.com/juancarlospaco/peewee-extra-fields) (拆分了原有的extra fields)，使用 `SimplePasswordField`

> Peewee `PasswordField` re-implemented and simplified from 2.x Versions to work with Peewee 3 and Python 3 using new `secrets` and `hashlib` from standard library, without dependencies, dont need `bcrypt`, internally uses `hashlib.pbkdf2_hmac()` and `secrets.compare_digest()`. Migration from `PasswordField` to `SimplePasswordField` is recommended when possible.

`SimplePasswordField` from peewee_extra_fields
只存储hash值，没有像 `werkzeug.security.generate_password_hash` 一样存储算法、盐。先用 Werkzeug 顶着较好，有时间自己改写类。

### redis 异步查询
redis 作为内存数据库，查询速度已经足够快，没太多必要使用异步查询。

但并不是没有redis异步插叙方案，搜索 aioredis.

### peewee 数据库迁移
没有可行方案，下次换 SQLAlchemy。

#### peewee_migrate
[peewee_migrate](https://github.com/klen/peewee_migrate) 此库更新最久，开发实时间最长

```
$ pw_migrate --help

Usage: pw_migrate [OPTIONS] COMMAND [ARGS]...

Options:
    --help  Show this message and exit.

Commands:
    create   Create migration.
    migrate  Run migrations.
    rollback Rollback migration.
```

冲突，安不上。需要使用 peewee-aync 0.6+。`peewee >= 3.3.1`

usage

- [MySQL ORM peewee的数据库迁移管理peewee_migrate](https://www.ctolib.com/topics-134262.html)
- [使用peewee_migrate来进行数据库结构的自动迁移](https://blog.csdn.net/a447685024/article/details/61644139)


非常不成熟，而且开发不活跃。目前不支持从单文件中最终Model变化，暂不使用。

#### peewee-db-evolve
[peewee-db-evolve](https://github.com/keredson/peewee-db-evolve)

不记录每次变动，只是滚动更新你的数据库schema。会弹出确认

非常垃圾，对于模型拆分、database从别处引入的情况没成功。

### 对接前端
跨域时（如本地直接打开HTML文件）浏览器会先尝试 OPTIONS 请求。

### JWT
[前后端分离之JWT用户认证](https://lion1ou.win/2017/01/18/)

cookies, session 向结合，保存用户状态。

token的问题

> 如果我们的页面出现了 XSS 漏洞，由于 cookie 可以被 JavaScript 读取，XSS 漏洞会导致用户 token 泄露，而作为后端识别用户的标识，cookie 的泄露意味着用户信息不再安全。
>
> 在设置 cookie 的时候，其实你还可以设置 httpOnly 以及 secure 项。设置 httpOnly 后 cookie 将不能被 JS 读取，浏览器会自动的把它加在请求的 header 当中，设置 secure 的话，cookie 就只允许通过 HTTPS 传输。secure 选项可以过滤掉一些使用 HTTP 协议的 XSS 注入，但并不能完全阻止。
>
> httpOnly 选项使得 JS 不能读取到 cookie，那么 XSS 注入的问题也基本不用担心了。但设置 httpOnly 就带来了另一个问题，就是很容易的被 XSRF，即跨站请求伪造。

如果 token 验证信息存储在数据库中，加大了服务器存储、查询开销。按照一定规律生成 token，服务器拿到后再解密。

JWT 可以使用 HMAC 算法或者是 RSA 的公钥密钥对进行签名。根据签名判断数据有没有被修改。因为根据加密、解密，完全**不需要存储到数据库**。

Flask 中 `itsdangerous.TimedJSONWebSignatureSerializer` 为类似的东西，有过期时间的token。

JWT用于设计用户认证和授权系统，甚至实现Web应用的单点登录。

> 单点登录（Single Sign On），简称为 SSO，是目前比较流行的企业业务整合的解决方案之一。SSO的定义是在多个应用系统中，用户只需要登录一次就可以访问所有相互信任的应用系统。
>
> 客户端持有ID，服务端持有session，两者一起用来保持登录状态。

单点登录实现方式

- 服务器共享session
- SSO-Token，所有服务器可验证 Token 有效性
- 浏览器将身份标识（session id，或者 token）存储到顶级域名cookies中，网站通过共同域名“共享cookie”。

### 集成 JWT 登录
JWT是加密？我的乖乖，视频主是要坑死多少新人。跟我念三遍：JWT是签名，JWT是签名，JWT是签名。

## 11 小组相关功能开发
- 新建小组
- model_to_dict 列出小组
- 申请加入小组
- 帖子：创建帖子，单个帖子详细信息
- 小组详情页面：小组信息、小组帖子
- 回复评论
- 为评论点赞

Note: 作者多处忘记增加计数，如帖子Post发布后增加Group的帖子数，评论发布后增加Post对应的评论数。

### authenticated 装饰器
梳理一下， `authenticated` 查找 `self.current_user`, `self.current_user` 查找 `self._current_user` 属性和 `self.get_current_user()`。

若经过上述步骤还没有找到用户信息，`self.get_login_url()` 重定向用户到登录页面。`self.get_login_url` 实际查找 `self.application.settings["login_url"]`.

注意

- `self.get_current_user()` 默认为空，需要用户重写
- `@authenticated` 在当前项目中需要重写为异步装饰器

### 用户认证
本教程中前后端完全分离，用户认证基于token，或者说基于 Header `tsessionid` 中的token信息。

### aiofiles 存储上传的文件
[aiofiles](https://github.com/Tinche/aiofiles/)

存储的文件名要随机化，避免冲突。因为非图床，没有下载需求，原文件名不需要保存。

将用户上传数据与前端静态文件分离开来。

### UEditor 富文本编辑器
本教程中不涉及，已经配置好。但是需要部署

- 前端域名与后端域名保持一致（否则上传功能无法）

注意启用 X-Frame-Options 允许同源。

例如，借助 nginx `add_header` 修改响应头。或者是 tornado `.set_header` 函数。

Nginx  `more_clear_headers 'Server';` 模块可以用来清理header。

```nginx
more_set_headers 'X-MyHeader: blah' 'X-MyHeader2: foo';
```

### peewee ORM 做复杂连接查询
```python
class Comment(BaseModel):
    """既代表帖子的评论，也代表对于另外一个评论的回复"""

    class Meta:
        table_name = "comments"

    user = ForeignKeyField(User, verbose_name="楼主", backref="comments")
    post = ForeignKeyField(Post, verbose_name="帖子", backref="comments")
    commented = ForeignKeyField(
        "self", verbose_name="回复此评论", related_name="commenter", null=True
    )
    # replied 属于冗余存储，但是可以减少表的查询压力
    replied = ForeignKeyField(
        User, verbose_name="答复此人", related_name="replier", null=True
    )
    body = CharField(max_length=1000, verbose_name="回复内容", null=False)
    reply_num = IntegerField(default=0, verbose_name="回复数")
    like_num = IntegerField(default=0, verbose_name="点赞数")

    @classmethod
    def extend(cls):
        # 多表join
        # 多字段映射同意个Model
        # alias
        user = User.alias()
        replied = User.alias()
        return (
            cls.select(
                cls, Post, user.id, user.nickname, replied.id, replied.nickname
            )
            .join(Post, join_type=JOIN.LEFT_OUTER, on=cls.post)
            .switch(cls)
            .join(user, join_type=JOIN.LEFT_OUTER, on=cls.user)
            .switch(cls)
            .join(replied, join_type=JOIN.LEFT_OUTER, on=cls.replied)
        )
```

### peewee-async 更新模型实例
```python
group = await self.application.objects.get(Group, id=int(group_id))
group.post_num += 1
await self.application.objects.update(group, only=["post_num"])
```

## 12 问答相关功能开发
纯业务，没什么新知识点

目前存在的一些问题

- 12-3，点个吊的按钮，questionList 页面排序、分类的点击触发你都还没做好吗！
- 12-4，问题详情页面拿到图片地址，但是没有渲染图片。另外没有获取单独的问题，而是尝试获取所有问题列表，渲染时固定渲染列表中最新的问题。

