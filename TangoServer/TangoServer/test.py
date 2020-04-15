"""
Simulate requests from client.
"""

import json
import os
import threading
import time
import pyodbc
import unittest
import requests

from TangoServer import HttpServer
from TangoServer import Frame
from TangoServer import config
from TangoServer.setup import setup


class TangoServerTest(unittest.TestCase):
    def setUp(self):
        setup()
        self.server = HttpServer.HttpServer((config.HOST, config.POST))
        self.t = threading.Thread(target=self.server.run).start()
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=localhost;DATABASE=TangoUsers;'
                              'UID=' + config.database_username +
                              ';PWD=' + config.database_password)
        self.cursor = cnxn.cursor()

    def test_generate_response(self):
        re = HttpServer.generate_response("200 OK", "nothing")
        respect = "HTTP/1.1 200 OK\r\nContent-Length: 7\r\n\r\nnothing"
        self.assertEqual(re, respect)

    def test_get_word_pool_list(self):
        # 向本机发出get_word_pool_list的请求，
        # 将返回的list与本机..\\Resource\\word_pool目录下的文件list做对比，
        # 如果相同则通过测试。
        r = requests.get('http://' + config.HOST + ':' + str(config.POST) + '/script=word_pool_list')
        word_loop_list = eval(r.text)
        word_loop_list_respect = os.listdir('..\\Resource\\word_pool')
        self.assertEqual(word_loop_list, word_loop_list_respect)

    def test_get_csv(self):
        # 向本机发出get_csv的请求，
        # 将返回的csv与本机直接打开的同一csv文件做对比，
        # 如果相同则通过测试。
        r = requests.get('http://' + config.HOST + ':' + str(config.POST) + '/getcsv=test.csv')
        try:
            test_csv = open('..\\Resource\\word_pool\\test.csv', 'rb')
        except Exception as err:
            self.assertTrue(False, err)
        else:
            content_respect = test_csv.read()
            self.assertEqual(r.content, content_respect)
            test_csv.close()

    def test_register(self):
        # 向本机发出register请求，注册一个用户，
        # 然后用注册信息查看本地TangoUser数据库中是否存在该用户信息（即是否成功注册），
        # 如果存在则注册成功
        username = 'test' + str(time.time())
        password = 'test' + str(time.time())
        requests.post('http://' + config.HOST + ':' + str(config.POST) + '/register',
                      data=json.dumps({'username': username,
                                       'password': password}))

        self.cursor.execute(
            'Select * From Users Where username = \'{}\' and password = \'{}\''.format(username, password))
        row = self.cursor.fetchone()
        if row:
            self.assertTrue(True)
        else:
            self.assertTrue(False, 'Fail to register.')

    def test_login(self):
        # 向本机发出login请求，登录test用户，
        # 然后查看用户是否在online_users中，
        # 如果存在则登录成功
        requests.post('http://' + config.HOST + ':' + str(config.POST) + '/login',
                      data=json.dumps({'username': 'test', 'password': 'test'}))
        if self.server.online_users.get('test') is None:
            self.assertTrue(False, 'Fail to log in.')
        else:
            self.assertTrue(True)

    def test_send_msg(self):
        # 向本机发出send_msg请求，使用test用户发送内容为test的信息，
        # 然后查看msg_list是否包含这条信息
        # 如果存在则发送成功
        data = json.dumps({'username': 'test', 'msg': 'test'})
        requests.post('http://' + config.HOST + ':' + str(config.POST) + '/send_msg', data=data)
        msg = Frame.Message('test', 'test')
        self.server.msg_list_lock.acquire()
        for message in self.server.msg_list:
            if message.content == msg.content and message.sender == msg.sender:
                self.server.msg_list_lock.release()
                self.assertTrue(True)
            else:
                self.server.msg_list_lock.release()
                self.assertTrue(False, 'Send message failed.')

    def tearDown(self):
        self.server.close()


if __name__ == '__main__':
    unittest.main()
