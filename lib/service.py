#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.orm import relationship, backref
from exceptions import TypeError

import base
Base = base.Base

# http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#association-pattern
# http://stackoverflow.com/questions/25958963/self-referential-association-relationship-sqlalchemy
class Service_tree(Base):
    __tablename__ = 'service_tree'
    parent_id = Column(Integer, ForeignKey('service.id'), primary_key=True)
    child_id = Column(Integer, ForeignKey('service.id'), primary_key=True)
    endpoint_id = Column(Integer, ForeignKey('endpoint.id'))
    stackpos = Column(Integer)
    endpoint = relationship('Endpoint', backref=backref('service_tree'))
    def __init__(self, parent, child, endpoint, stackpos=None):
        self.parent = parent
        self.child = child
        self.endpoint = endpoint
        if not stackpos and endpoint.stackpointer:
            self.stackpos = endpoint.stackpointer
        elif not stackpos and not endpoint.stackpointer:
            raise TypeError('stackpos not set')
        else:
            self.stackpos = stackpos

    def get_state(self):
        state = {}
        state['parent'] = self.parent.name
        state['child'] = self.child.name
        state['endpoint'] = self.endpoint.name
        state['stackpos'] = self.stackpos
        return state


class Service(Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    port = Column(Integer, nullable=False, unique=True)
    parents = relationship('Service_tree', backref='child', primaryjoin=id==Service_tree.child_id)
    childs = relationship('Service_tree', backref='parent', primaryjoin=id==Service_tree.parent_id)

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
        state['parent'] = [parent.get_state() for parent in self.parents]
        state['childs'] = [child.get_state() for child in self.childs]
        return state


if __name__ == '__main__':
    s = Service("hest")
    print type(s)
    s.name = "Hest"
    print s.name
