"""
set basic configuration
"""
import json
from TangoClient import config


def setup():
    json_file = open("config.json", 'r')
    conf = json_file.read()
    conf = json.loads(conf)
    config.Server = str(conf["Server"])
    config.POST = str(conf["POST"])
    json_file.close()


if __name__ == '__main__':
    setup()
