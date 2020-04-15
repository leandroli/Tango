"""
Init a HttpServer and run it.
"""

from TangoServer.HttpServer import HttpServer
from TangoServer import config
from TangoServer.setup import setup

if __name__ == '__main__':
    setup()
    http_server = HttpServer((config.HOST, config.POST))
    http_server.run()
