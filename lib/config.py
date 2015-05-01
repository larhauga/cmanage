#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import logging, logging.config
from os import path
from sys import exit

basepath = path.split(path.dirname(path.abspath(__file__)))[0]
configpath = path.join(basepath, 'etc/config.conf')
logconfigpath = path.join(basepath, 'etc/logging.conf')

if path.isfile(configpath):
    config = ConfigParser.ConfigParser()
    config.read(configpath)
else:
    logging.error("Missing configuration file %s" % configpath)
    exit(1)

if path.isfile(logconfigpath):
    logging.config.fileConfig(logconfigpath)
    logger = logging.getLogger('main')
else:
    logging.error("Missing logger configuration file %s" % logconfigpath)
    exit(1)

def get_config():
    return config

def get_logger():
    return logging
