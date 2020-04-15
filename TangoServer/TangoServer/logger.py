"""
A simple logger for tango server
"""

import logging


class TangoServerLogger(object):

    def __init__(self, file_path: str = "..\\Resource\\log.txt", name: str = 'TangoServerLogger'):
        """
        Create a logger and set the basic configuration.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        logfile = logging.FileHandler(file_path)
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)

        self.logger.addHandler(logfile)

    def debug(self, msg):
        """
        Log msg with severity 'DEBUG'.
        """
        self.logger.debug(msg)

    def info(self, msg):
        """
        Log msg with severity 'INFO'.
        """
        self.logger.info(msg)

    def warning(self, msg):
        """
        Log msg with severity 'WARNING'.
        """
        self.logger.warning(msg)

    def error(self, msg):
        """
        Log msg with severity 'ERROR'.
        """
        self.logger.error(msg)

    def critical(self, msg):
        """
        Log msg with severity 'CRITICAL'.
        """
        self.logger.critical(msg)
