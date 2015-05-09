#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, MetaData,ForeignKey, text
from sqlalchemy.orm import relationship, backref

import base
Base = base.Base


class Endpoint(Base):
    __tablename__ = 'endpoint'

    id = Column(Integer, primary_key = True)
    name = Column(String, unique=True)
    ip = Column(String)
    pubport = Column(Integer, unique=True, nullable=False)
    url = Column(String)
    stackpointer = Column(Integer)#, nullable=False)  # Inteneded as default placement on stack
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)
    stage = Column(String)
    #stage_id = Column(Integer, ForeignKey('stage.id'))
    #stage = relationship('Stage', backref=backref('endpoint'))

    def __init__(self, name, service, pubport, stackpointer=None, stage=None):
        self.name = "%s-endpoint-%s" % (service.name, name)
        self.service = service
        self.pubport = pubport
        self.stackpointer = stackpointer
        self.stage = stage

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['ip'] = self.ip
        state['pubport'] = self.pubport
        state['url'] = self.url
        state['stage'] = self.stage
        state['service'] = self.service.name
        state['stackpointer'] = self.stackpointer
        return state


if __name__ == '__main__':
    e = endpoint("hest")
    print type(e)
    e.name = "Hest"
    print e.name
