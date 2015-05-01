#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

import base
Base = base.Base


class Stack(Base):
    __tablename__ = 'stack'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    host = Column(String)
    service_id = Column(Integer, ForeignKey('service.id'))
    container = relationship('Container', backref=backref('stack'),
                             order_by='Container.id')

    def __init__(self, name, service, host=None):
        """Creates a stack from a service
        Arguments:
            name: Name of stack
            service: Parent service object
            host: Machine the stack exists on
        """
        self.name = name
        self.service = service
        self.host = host

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['container'] = []
        for container in self.container:
            state['container'].append(container.get_state())
        return state
