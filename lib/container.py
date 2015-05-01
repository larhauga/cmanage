#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from exceptions import LookupError

import base
Base = base.Base


class Container(Base):
    """ Class for containers """
    __tablename__ = 'container'

    id = Column(Integer, primary_key=True)
    name = Column(String)     # The name the container will have
    version = Column(String)  # 'version'
    image = Column(String)    # 'image' without version
    # source_image = Column(String)
    # ip = Column(String)  # The local ip
    port = Column(String)  # The local port
    stack_id = Column(Integer, ForeignKey('stack.id'))
    stage_id = Column(Integer, ForeignKey('stage.id'))
    stage = relationship('Stage', backref=backref('container'))

    def __init__(self, stack, version, image=None, name='app'):
        """Creates a new container object
        Arguments:
            stack: stack object of parent stack
            version: version of image

        Keyword arguments:
            image: name of container image (when None: from stack): LookupError
        Sets:
            name: based on stackname + app + nr, if set (chagnes app)
        """
        self.stack = stack
        if not image:
            if stack.image:
                self.image = stack.image
            else:
                raise LookupError('No image defined in stack or init')
        else:
            self.image = image
        self.name = '%s-%s%s' % (self.stack.name, name,
                                 len(self.stack.container))


    def __repr__(self):
        return self.name

    def get_version(self):
        return "{}:{}".format(self.image, self.version)

    def get_state(self):
        state = {}
        state['name'] = self.name
        state['version'] = self.version
        state['image'] = self.image
        # state['source_image'] = self.source_image
        # state['ip'] = self.ip
        state['port'] = self.port
        state['stage'] = self.stage
        return state

if __name__ == '__main__':
    c = container()
