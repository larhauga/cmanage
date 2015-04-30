#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
# from sqlalchemy.ext.declarative import declarative_base

import base
Base = base.Base


class Container(Base):
    """ Class for containers """
    __tablename__ = 'container'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    image = Column(String)
    source_image = Column(String)
    ip = Column(String)  # The local ip
    port = Column(String)  # The local port
    stack_id = Column(Integer, ForeignKey('stack.id'))
    # stack = relationship('Stack', backref=backref('stack'))
    stage_id = Column(Integer, ForeignKey('stage.id'))
    stage = relationship('Stage', backref=backref('container'))

    def __init__(self, name, stack):
        self.name = name
        self.stack = stack

    def __repr__(self):
        return self.name

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['version'] = self.version
        state['image'] = self.image
        state['source_image'] = self.source_image
        state['ip'] = self.ip
        state['port'] = self.port
        state['stage'] = self.stage
        return state

if __name__ == '__main__':
    c = container()
