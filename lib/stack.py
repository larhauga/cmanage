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
    image = Column(String)
    service_id = Column(Integer, ForeignKey('service.id'))
    container = relationship('Container', backref=backref('stack'),
                             order_by='Container.id')

    def __init__(self, service, image, host=None):
        """Creates a stack from a service
        Arguments:
            service: Parent service object
            host: Machine the stack exists on
        Sets:
            name: service name and len of stack
        """
        self.service = service
        self.name = '%s-stack%s' % (self.service.name, len(self.service.stacks))
        self.host = host
        self.image = image

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['container'] = []
        for container in self.container:
            state['container'].append(container.get_state())
        return state
