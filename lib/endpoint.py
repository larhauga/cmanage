#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, MetaData,ForeignKey, text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import base
Base = base.Base

class Endpoint(Base):
    __tablename__ = 'endpoint'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    ip = Column(String)
    port = Column(String)
    url = Column(String)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)
    #service = relationship('Service', backref=backref('endpoint'))
    stage_id = Column(Integer, ForeignKey('stage.id'))
    stage = relationship('Stage', backref=backref('endpoint'))

    def __init__(self, name, service):
        self.name = name
        self.service = service

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['ip'] = self.ip
        state['port'] = self.port
        state['url'] = self.url
        state['stage'] = self.stage.name
        state['service'] = self.service.name
        return state


if __name__ == '__main__':
    e = endpoint("hest")
    print type(e)
    e.name = "Hest"
    print e.name
