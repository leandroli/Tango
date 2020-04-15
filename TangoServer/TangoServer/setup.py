"""
set basic configuration
"""
import json
from TangoServer import config


def setup():
    json_file = open("config.json", 'r')
    conf = json_file.read()
    conf = json.loads(conf)
    config.database_password = str(conf["database_password"])
    config.database_username = str(conf["database_username"])
    config.HOST = str(conf["HOST"])
    config.POST = conf["POST"]
    json_file.close()


if __name__ == '__main__':
    setup()
