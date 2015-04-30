#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import base
Base = base.Base
#Base = declarative_base()

parents = Table(
    'parents_rel', base.Base.metadata,
    Column('parent_id', Integer, ForeignKey('service.id'), primary_key=True),
    Column('service_id', Integer, ForeignKey('service.id'), primary_key=True),
    Column('endpoint_id', Integer, ForeignKey('endpoint.id'))
)


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    port = Column(Integer, nullable=False, unique=True)
    # parent services ?
    #parent_id = Column(Integer, ForeignKey('service.id'))
    childs = relationship('Service', secondary=parents,
                      primaryjoin=id == parents.c.parent_id,
                      secondaryjoin=id == parents.c.service_id, backref='parents')

    # child services ?gg
    stacks = relationship('Stack', backref=backref('service', order_by=id))
    endpoints = relationship('Endpoint', backref=backref('service'))
    #tree

    def __init__(self, name, port):
        self.name = name
        self.port = port

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['port'] = self.port
        #state['stacks'] = [s.get_state() for s in self.stacks]
        state['stacks'] = []
        for stack in self.stacks:
            state['stacks'].append(stack.get_state())
        return state

    #@property
    #def name(self): return self.name

    #@name.setter
    #def name(self, name): self.name = name


if __name__ == '__main__':
    s = Service("hest")
    print type(s)
    s.name = "Hest"
    print s.name
