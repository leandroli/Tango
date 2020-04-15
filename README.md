# Taogo

一款用于背单词的pc软件(附有聊天室功能), 客户端采用tkinter, 服务器端实现了一个简单的webserver.

## 整体架构

### Tango Server--服务器端架构

![](.\snapshots\README1.png)

为了更简单的添加功能和解耦，选择了给服务器端分层，将于客户端进行交互的部分（维护在线用户、发送csv文件，接收消息等直接用到socket的部分）单做一层，作为HttpServer与客户端进行互交，然后用这个部分调用Frame部分中的类来实现各部分功能。这样就很容易在Frame部分添加新的功能而不用直接跟socket打交道，可以更好的解耦，便于扩展功能。

1. Frame部分定义了用户类和消息类，在用户类中有注册和判断能否正常登录（用户名存在且密码正确）的方法，这些方法和SQL server互交进行用户信息的增删改查。
2. Logger模块用于记录系统的状态，包含了各种各样的信息。日志信息分为5个等级：

```
1.	CRITICAL - 严重错误
2.	ERROR - 一般错误
3.	WARNING - 警告信息
4.	INFO - 一般信息
5.	DEBUG - 调试信息
```

​	如果系统出现BUG可以通过记录的日志进行分析解决。

3. 自动化单元测试test模块可以对服务器端进行自动化的单元测试。运行test.py即可对服务器的基本功能（显示可用词库、下载词库、注册、登录、发送消息等）进行自动测试，如果对服务器端有改动，可以运行test.py测试基本功能，保证基本功能可以正常运行。运行示例：（成功）

```
......
----------------------------------------------------------------------
Ran 6 tests in 1.534s

OK
```

留言板（聊天室）模块可以完成对用户留言的实时更新，把留言广播给每个用户，提供给用户进行交流的功能

### Tango Client--客户端流程

![](.\snapshots\README2.png)

## 工程文件组织结构

```
(TangoServer)
.
├── Resource
│   ├── log.txt
│   └── word_pool
│       └── Japanese_word.csv
├── TangoServer
│   ├── Frame.py
│   ├── HttpServer.py
│   ├── WordFilePrehandle.py
│   ├── config.json
│   ├── config.py
│   ├── logger.py
│   ├── main.py
│   ├── setup.py
│   └── test.py
```

1. TangoServer文件夹下存放源文件，WordFilePrehandle.py文件对初始的单词文件进行格式化。setup.py文件对config模块的设置进行初始化。

2. Resource文件夹下存放进行记录的日志文件，wordpool文件夹存放各单词文件。

```
(TangoClient)
.
├── Resource
│   ├── TangoLogger.log
│   ├── data
│   │   ├── a.tangomemory
│   │   ├── aaaa.tangomemory
│   │   ├── qqq.tangomemory
│   │   ├── qqqq.tangomemory
│   │   ├── r.tangomemory
│   │   └── test.tangomemory
│   ├── word_pool
│   │   ├── Japanese_word.csv
│   │   ├── Japanese_word2.csv
│   └── word_pooltest_word.csv
├── TangoClient
│   ├── client.py
│   ├── config.json
│   ├── config.py
│   ├── logger.py
│   ├── main.py
│   ├── setup.py
│   ├── test.py
│   └── user.py
└── main.spec
```

与服务器端相同，TangoClient文件夹下存放源文件，config.json文件存放客户端的设置，在Resource文件夹下还记录了用户数据，用来标记记住了和没记住的单词。

## HttpServer模块各接口的描述

### Init初始化

```python
def __init__(self, server_addr, bind_and_activate=True):
        """
     Set basic configuration of the server.

     To pass address information, use argument server_addr.

     If you do not want to let server bind and activate automatically,
     set the argument bind_and_activate to False.
     """
```

### bind绑定监听套接字

```python
def bind(self):
        """
        Bind Server to its post.
        """
```

### activate激活监听套接字

```python
def handle(self, client_socket):
        """
        Handle all requests in this method,
        it will call other method to do detail.

        Argument "client_socket" is address of the client this method serve.

        It response only two kinds of HTTP requests: GET and POST.
        The GET requests should request like getcsv=xxx.csv or script = some_script.
        The POST requests should request like login, register, send_msg, log_out.

        This method will not exit until client cut down the connection or the server is going to close.
        """
```

### run启动该服务器

```python
def run(self):
        """
        Start running server.

        If you want to quit, please input quit command in terminal.
        """
```

### close关闭服务器，停止服务

```python
def close(self):
        """
        Close all socket this server is preserving.
        """
```

## 操作说明

### 操作流程

![](.\snapshots\README3.png)

### 留言板界面

<img src=".\snapshots\README4.png" style="zoom:60%;" />

### 单词记忆界面（点击start后）

<img src=".\snapshots\README5.png" style="zoom:50%;" />

<img src=".\snapshots\README6.png" style="zoom:60%;" />