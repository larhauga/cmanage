#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from exceptions import TypeError

import config as cfg
containerconfig = cfg.get_container_config()

import base
Base = base.Base


# http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#association-pattern
# http://stackoverflow.com/questions/25958963/self-referential-association-relationship-sqlalchemy
class Service_tree(Base):
    __tablename__ = 'service_tree'
    parent_id = Column(Integer, ForeignKey('service.id'), primary_key=True)
    child_id = Column(Integer, ForeignKey('service.id'), primary_key=True)
    endpoint_id = Column(Integer, ForeignKey('endpoint.id'), primary_key=True)
    stackpos = Column(Integer)
    endpoint = relationship('Endpoint', backref=backref('service_tree'))
    port = Column(Integer)

    def __init__(self, parent, child, endpoint, stackpos=None):
        self.parent = parent
        self.child = child
        self.endpoint = endpoint
        if stackpos >= 0:
            self.stackpos = stackpos
        elif endpoint.stackpointer >= 0:
            self.stackpos = endpoint.stackpointer
        elif not stackpos and not endpoint.stackpointer:
            raise TypeError('stackpos not set')

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
    parents = relationship('Service_tree', backref='child',
                           primaryjoin=id == Service_tree.child_id)
    childs = relationship('Service_tree', backref='parent',
                          primaryjoin=id == Service_tree.parent_id)
    stacks = relationship('Stack', cascade="delete",
                          backref=backref('service', order_by=id))
    endpoints = relationship('Endpoint', backref=backref('service'))

    def __init__(self, name):
        self.name = name

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['stacks'] = []
        for stack in self.stacks:
            state['stacks'].append(stack.get_state())
        state['parent'] = [parent.get_state() for parent in self.parents]
        state['childs'] = [child.get_state() for child in self.childs]
        state['endpoints'] = [e.name for e in self.endpoints]
        return state

    def choose_host(self):
        """Finds out which server a stack should run on based on current stacks
        Simple implementation. Implement on first host first
        """
        hosts = containerconfig.get('main', 'hostnames').split(',')
        if self.stacks:
            # if even
            if len(self.stacks) % 2 == 0:
                return hosts[0]
            # if odd
            elif len(self.stacks) % 2 == 1:
                return hosts[1]
        else:
            # No existing stacks
            return hosts[0]

    def tree_on_stack_pointer(self, stackpointer):
        for parent in self.parents:
            if parent.stackpos == stackpointer:
                return parent.endpoint
        return None

if __name__ == '__main__':
    s = Service("hest")
    print type(s)
    s.name = "Hest"
    print s.name
