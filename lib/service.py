#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.orm import relationship, backref

import base
Base = base.Base

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
    childs = relationship('Service', secondary=parents,
                          primaryjoin=id == parents.c.parent_id,
                          secondaryjoin=id == parents.c.service_id,
                          backref='parents')

    stacks = relationship('Stack', backref=backref('service', order_by=id))
    endpoints = relationship('Endpoint', backref=backref('service'))

    def __init__(self, name, port):
        self.name = name
        self.port = port

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['port'] = self.port
        state['stacks'] = []
        for stack in self.stacks:
            state['stacks'].append(stack.get_state())
        state['parent'] = [parent.name for parent in self.parents]
        state['childs'] = [child.name for child in self.childs]
        return state


if __name__ == '__main__':
    s = Service("hest")
    print type(s)
    s.name = "Hest"
    print s.name
