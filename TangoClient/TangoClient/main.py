"""
The main function of client server
"""

from TangoClient.client import Tango
from TangoClient.setup import setup
from TangoClient import config


def main():
    setup()
    T = Tango()
    T.server_addr = config.Server + ":" + config.POST
    T.initUI()


if __name__ == '__main__':
    main()
