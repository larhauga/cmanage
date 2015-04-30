#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import base
Base = base.Base
#Base = declarative_base()

class Stack(Base):
    __tablename__ = 'stack'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    service_id = Column(Integer, ForeignKey('service.id'))
    #service = relationship('Service', backref=backref('stack', order_by=name))
    container = relationship('Container', backref=backref('stack'), order_by='Container.id')
    # containers

    def __init__(self, name, service):
        self.name = name
        self.service = service

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['container'] = []
        for container in self.container:
            state['container'].append(container.get_state())
        return state
