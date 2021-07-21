#  :copyright: Copyright (c) 2018-2020. OS4D Ltd - All Rights Reserved
#  :license: Commercial
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Written by Stefano Apostolico <s.apostolico@gmail.com>, October 2020
import logging

from time import sleep
from bitcaster_sdk import trigger, init, logger


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format = '%(levelname)-8s %(filename)-12s:%(lineno)d - %(funcName)8s() - %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = CustomFormatter('%(levelname)8s - %(filename)15s %(funcName)8s - %(message)s')
ch.setFormatter(formatter)
logger.handlers = []
logger.addHandler(ch)

if __name__ == '__main__':
    init("http://31a4284b99ad54b08396ccffa5662698c96d9cac21f54a67b454e94f2c5fbe65@localhost:8000/api/o/bitcaster/a/38/",
         debug=True)
    num = 0
    while True:
        num += 1
        trigger(26)
        logger.debug(f"runner cycle ")
        sleep(10)
