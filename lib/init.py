#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from os import path

import base
import config as cfg
from service import Service
from stack import Stack
from container import Container
from endpoint import Endpoint
from stage import Stage

logging = cfg.get_logger()
config = cfg.get_config()

def init(create=False):
    Base = base.Base

    engine = create_engine(config.get('database','engine'),
                           echo=config.getboolean('database','echo'))

    Session = sessionmaker(bind=engine)
    session = Session()
    if create:
        Base.metadata.create_all(engine)
    return session


def base_test_data(session, servicename,pubport):
    s = Service(servicename)
    for i in range(1,3):
        webstack = Stack(s, 'image')
        session.add(s)
        session.add(webstack)
        for i in range(1, 10):
            c = Container(webstack, 'v0.%s' % i)
            session.add(c)
        session.commit()

    session.commit()

    s = session.query(Service).filter(Service.name == servicename).first()
    e = Endpoint('web', s, pubport)
    session.add(e)
    session.commit()


def get_state(session, service):
    s = session.query(Service).filter(Service.name == service).first()
    print s
    if s:
        endpoint = s.endpoints
        print endpoint
        print s.name
        for stack in s.stacks:
            for container in stack.container:
                print container.name


def main():
    session = init(create=True)
    base_test_data(session, 'webapp1', 1010)
    base_test_data(session, 'webapp2', 1020)

    get_state(session, 'webapp1')
    get_state(session, 'webapp2')

if __name__ == '__main__':
    main()
