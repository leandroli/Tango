"""
A simple http server model to serve requests from TangoClient.

Last update: 12.22.2019 LIZHUO
"""

# coding=utf-8
import socket
import re
import threading
from threading import Semaphore
from TangoServer import Frame
import time
from TangoServer.logger import TangoServerLogger


def generate_response(header, body):
    """
    generate_response(header, body) -> str: response

    Return a complete response with argument header and body.

    Example:
        generate_response('404 NOT FOUND', 'FILE NOT FOUND')
    """
    response_header = "HTTP/1.1 {}\r\n".format(header)
    response_header += "Content-Length: %d\r\n" % (len(body.encode('utf-8')))
    response_header += "\r\n"
    return response_header + body


class HttpServer(object):

    request_queue_size = 10
    ID_count = 1

    def __init__(self, server_addr, bind_and_activate=True):
        """
        Set basic configuration of the server.

        To pass address information, use argument server_addr.

        If you do not want to let server bind and activate automatically,
        set the argument bind_and_activate to False.
        """

        self.server_addr = server_addr

        # listening on this socket
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket_list = []
        self.client_socket_list_lock = threading.Lock()

        # store all message in this list
        self.msg_list = []
        self.msg_list_lock = threading.Lock()

        # all online users, cannot log in when this user is already online
        self.online_users = {}
        self.online_users_lock = threading.Lock()

        self.logger = TangoServerLogger(name=f'TangoServer{HttpServer.ID_count}')
        self._logger = Semaphore(1)

        self._close_flag = 0
        self._close_flag_lock = threading.Lock()

        if bind_and_activate is True:
            try:
                self.bind()
                self.activate()
            except Exception as err:
                self.close()
                raise err

        self.__log(self.logger.critical, f'TangoServer{HttpServer.ID_count} is started')
        HttpServer.ID_count += 1

    def bind(self):
        """
        Bind Server to its post.
        """
        self.__log(self.logger.debug, "Start to bind...")
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(self.server_addr)
        self.__log(self.logger.debug, "Successfully bind" + str(self.server_addr))

    def activate(self):
        """
        Activate the server(start listening to request from client).
        """
        self.listen_socket.listen(self.request_queue_size)
        self.__log(self.logger.debug, "Start listening...")

    def __log(self, log_operation, msg):
        # Log safely with a semaphore
        self._logger.acquire()
        log_operation(msg)
        self._logger.release()

    def __handle_csv_request(self, client_socket, request):
        """
        Handle request of download csv file.

        The argument "request" should be xxx.csv
        """
        try:
            self.__log(self.logger.debug, f'Try to find and open the cvs file. FILENAME: {request}')
            word_pool = open('../Resource/word_pool/' + request, 'rb')

        except Exception as err:

            response_body = "------file not found-----"

            response_header = "HTTP/1.1 404 NOT FOUND\r\n"
            response_header += "Content-Type: csv; charset=utf-8\r\n"
            response_header += "Content-Length: %d\r\n" % (len(response_body))
            response_header += "\r\n"

            response = response_header + response_body
            client_socket.send(response.encode('utf-8'))

            self.__log(self.logger.error, err)

        else:
            response_body = word_pool.read()  # word_pool文件大的情况下不能直接读，需要分开发
            word_pool.close()
            response_header = "HTTP/1.1 200 OK\r\n"
            response_header += "Content-Type: csv; charset=utf-8\r\n"
            response_header += "Content-Length: %d\r\n" % (len(response_body))
            response_header += '\r\n'

            response = response_header + response_body.decode('utf-8')
            client_socket.send(response.encode('utf-8'))

            self.__log(self.logger.info, f"Send {request} to client successfully.")

    def __handle_msg(self, msg):
        # add a message into msg_list
        self.msg_list_lock.acquire()
        self.msg_list.append(msg)
        self.msg_list_lock.release()

    def __send_msg(self, client):
        """
        Send message to client
        """

        self.msg_list_lock.acquire()

        # get all messages into response body
        response_body = ''
        for msg in self.msg_list:
            response_body += str(msg)

        self.msg_list_lock.release()

        self.__log(self.logger.info, f'Send [{response_body}] to {client.getpeername()}')
        client.send(generate_response('200 OK', response_body).encode('utf-8'))

    def __handle_script_request(self, client_socket, request):
        """
        Handle all script requests here.
        """
        if request == 'word_pool_list':
            # Send list of word pool to client.
            response_body = str(Frame.show_word_pool_list())
            client_socket.send(generate_response('200 OK', response_body).encode('utf-8'))
            self.__log(self.logger.info, f'Send list of word pool to {client_socket.getpeername()}')
        elif request == 'get_msg':
            # Send message to client
            self.__send_msg(client_socket)
        else:
            # Undefined script
            response_body = "------file not found-----"
            self.__log(self.logger.error, f'Do not have the script that {client_socket.getpeername()} requests.')
            client_socket.send(generate_response('404 NOT FOUND', response_body).encode('utf-8'))

    def __handle_post_option(self, client, option, content):
        """
        Handle post requests.

        Option can be: login, register, send_msg, log_out.
        Other options is undefined.

        Argument "content" contain user's information in dict format.
        """

        # get user information in to a dict
        user_dict = eval(content)

        if option == 'login':
            # ===================
            # log in
            # ===================
            user = Frame.User(user_dict['username'], user_dict['password'])
            self.__log(self.logger.info, f"User {user_dict['username']} try to login.")

            if user.can_log_in():
                self.online_users_lock.acquire()

                if self.online_users.get(user.username) is None:
                    self.online_users[user.username] = 1
                    self.online_users_lock.release()

                    response_body = 'Successfully log in.'
                    client.send(generate_response('200 OK', response_body).encode('utf-8'))
                    self.__log(self.logger.info, f"User {user.username} login.")
                else:
                    self.online_users_lock.release()

                    response_body = 'The user has logged in.'
                    client.send(generate_response('200 OK', response_body).encode('utf-8'))
                    self.__log(self.logger.info, f"User {user.username} has logged in.")

            else:
                response_body = 'The user is not exists.'
                client.send(generate_response('404 NOT FOUND', response_body).encode('utf-8'))
                self.__log(self.logger.info, f"User {user.username} fail to log in.")

        elif option == 'register':
            # ===================
            # register
            # ===================

            user = Frame.User(user_dict['username'], user_dict['password'])
            self.__log(self.logger.info, f"Client {client.getpeername()} try to register with: "
                                         f"User {user.username}.")

            if user.register():
                client.send(generate_response('200 OK', 'Successfully registered.').encode('utf-8'))
                self.__log(self.logger.info, f'User {user.username} register successfully.')
            else:
                client.send(generate_response('200 OK', 'The user name is existed.').encode('utf-8'))
                self.__log(self.logger.info, f'Client {client.getpeername()} fail to register.')

        elif option == 'send_msg':
            # ===================
            # send message
            # ===================

            self.__handle_msg(Frame.Message(user_dict['msg'], user_dict['username']))
            client.send(generate_response('200 OK', 'Successfully Received').encode('utf-8'))
            self.__log(self.logger.info, f'Send messages to {client.getpeername()}')

        elif option == 'log_out':
            # ===================
            # log out
            # ===================

            user = Frame.User(user_dict['username'], user_dict['password'])
            self.__log(self.logger.info, f"User {user.username} try to log out. From socket: {client.getpeername()}")
            self.online_users_lock.acquire()

            if self.online_users.get(user.username) is None:
                self.online_users_lock.release()

                client.send(generate_response('404 NOT FOUND',
                                              'Log out wrong. The user in not no line.').encode('utf-8'))
                self.__log(self.logger.info, f"User {user.username} is not online but try to log out."
                                             f" From socket: {client.getpeername()}")
            else:
                self.online_users.pop(user.username)
                self.online_users_lock.release()

                client.send(generate_response('200 OK', 'Successfully log out.').encode('utf-8'))
                self.__log(self.logger.info, f"User {user.username} successfully log out."
                                             f" From socket: {client.getpeername()}")

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

        # It is a important method that determine
        # what the request is and handle it properly.

        client_addr = client_socket.getpeername()
        while True:
            try:
                # Sleep 0.2 seconds to get a complete request from client.
                time.sleep(0.2)
                data = client_socket.recv(2048)
                data = data.decode('utf-8')
                self.__log(self.logger.info, f"Receive data from {client_addr}. DATA:[{data}]")

            except Exception as err:
                self.__log(self.logger.error, err)
                break

            else:
                # Truly receive the data to parse.
                data_lines = data.splitlines()

                try:
                    # Try to get what it request for.
                    match_result = re.match("([A-Z]+) /([^ ]*)", data_lines[0])

                except Exception as err:
                    self.__log(self.logger.error, err)
                    break

                else:
                    request = ""

                    if match_result.group(1) == 'GET':
                        request = match_result.group(2)
                        self.__log(self.logger.info, f"Request :GET from client: {client_addr}.")

                    elif match_result.group(1) == 'POST':
                        self.__log(self.logger.info, f"Request :GET from client: {client_addr}.")
                        option = match_result.group(2)

                        # Line i will be last line of request head after the loop
                        i = int()
                        for i in range(1, len(data_lines)):
                            if data_lines[i] == '':
                                break

                        try:
                            self.__handle_post_option(client_socket, option, data_lines[i + 1])

                        except Exception as err:
                            self.__log(self.logger.error, err)

                    if request.startswith('getcsv='):
                        # Get the name of csv file be requested and
                        # handle it with private method.

                        request = request[len('getcsv='):]
                        self.__handle_csv_request(client_socket, request)

                    elif request.startswith('script='):
                        # Get the name of script be requested and
                        # handle it with private method.

                        request = request[len('script='):]
                        self.__handle_script_request(client_socket, request)

                    else:
                        # Undefined request
                        self.__log(self.logger.error, f"Undefined request: {request} from client: {client_addr}.")
                        response_body = "------file not found-----"
                        response_header = "HTTP/1.1 404 NOT FOUND\r\n"
                        response_header += "Content-Type: text/html; charset=utf-8\r\n"
                        response_header += "Content-Length: %d\r\n" % (len(response_body))
                        response_header += "\r\n"
                        response = response_header + response_body
                        try:
                            client_socket.send(response.encode('utf-8'))
                        except Exception as err:
                            self.__log(self.logger.error, err)

        client_socket.close()

    def __wait_for_command(self):
        # Thread wait for quit command.
        while True:
            time.sleep(1)
            command = str(input())
            if command == 'quit':
                self._close_flag_lock.acquire()
                self._close_flag = 1
                self._close_flag_lock.release()
                break

    def run(self):
        """
        Start running server.

        If you want to quit, please input quit command in terminal.
        """

        threading.Thread(target=self.__wait_for_command).start()

        while True:
            # start a new thread for every client.
            try:
                client_socket, client_addr = self.listen_socket.accept()
            except Exception as err:
                self.__log(self.logger.error, err)
            else:
                self.client_socket_list_lock.acquire()
                self.client_socket_list.append(client_socket)
                self.client_socket_list_lock.release()

                threading.Thread(target=self.handle, args=(client_socket, )).start()

                self._close_flag_lock.acquire()
                if self._close_flag == 1:
                    self.close()
                    self._close_flag_lock.release()
                    break
                self._close_flag_lock.release()

    def close(self):
        """
        Close all socket this server is preserving.
        """
        self.client_socket_list_lock.acquire()
        for client_socket in self.client_socket_list:
            client_socket.close()
        self.client_socket_list_lock.release()
        self.listen_socket.close()


if __name__ == '__main__':
    HOST, POST = "127.0.0.1", 7000

    http_server = HttpServer((HOST, POST))
    http_server.run()

