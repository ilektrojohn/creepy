#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from utilities import XStream

class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        if record:
            XStream.XStream.stdout().write('{0}\n'.format(record))
