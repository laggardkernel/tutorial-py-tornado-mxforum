# Tornado打造高并发论坛
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
