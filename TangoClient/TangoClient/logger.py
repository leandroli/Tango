import logging


class Logger:
    def __init__(self, path, flevel=logging.DEBUG):
        """
        Create a logger and set the basic configuration.
        """
        # create logger
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)

        # create handler
        logfile = logging.FileHandler(path)

        # set the formatter of handler
        formatter = logging.Formatter('%(asctime)+s  %(name)+s  %(levelname)+s  %(message)+s')
        logfile.setFormatter(formatter)

        # add handler into logger
        self.logger.addHandler(logfile)

    def info(self, message):
        """
        Log message with severity 'INFO'.
        """
        self.logger.info(message)

    def debug(self, message):
        """
        Log message with severity 'DEBUG'.
        """
        self.logger.debug(message)

    def war(self, message):
        """
        Log message with severity 'WARNING'.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Log message with severity 'ERROR'.
        """
        self.logger.error(message)

    def cri(self, message):
        """
        Log message with severity 'CRITICAL'.
        """
        self.logger.critical(message)
