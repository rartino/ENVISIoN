#!/usr/bin/env python3

"""
TODO
"""

import sys

# TODO: Use actual enums.
LOG_NONE = 0
LOG_ERROR = 1
LOG_WARNING = 2
LOG_INFO = 3
LOG_DEBUG = 4
LOG_ALL = 1000

LOG_LEVEL_RAISE = LOG_ERROR
LOG_LEVEL_PRINT = LOG_ALL

def log(log_level, file_path, line_nr, message, message_data=None):
    """
    TODO.
    """
    if message_data:
        message = "{}: \"{}\"".format(message, message_data)
    log_level_str = {
            LOG_ERROR : "Error",
            LOG_WARNING : "Warning",
            LOG_INFO : "Info",
            LOG_DEBUG : "Debug",
        }[log_level]
    output = "{} : {} : {} : {}".format(file_path, line_nr, log_level_str, message)
    if log_level <= LOG_LEVEL_RAISE:
        raise ValueError(output)
    elif log_level <= LOG_LEVEL_PRINT:
        print(output, file=sys.stderr)

