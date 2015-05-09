#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from exceptions import LookupError
from random import getrandbits
from time import sleep

import base
Base = base.Base

import lib_docker as docker


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
    containerid = Column(String)
    stack_id = Column(Integer, ForeignKey('stack.id'))
    #stage_id = Column(Integer, ForeignKey('stage.id'))
    #stage = relationship('Stage', backref=backref('container'))

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
        if stack:
            self.stack = stack
            self.name = '%s-%s%s_0x%s' % (self.stack.name,
                                     name,
                                     len(self.stack.container), getrandbits(30))
        else:
            self.name = '%s_0x%s' % (name, getrandbits(30))
        if not image:
            if stack and stack.image:
                self.image = stack.image
            else:
                raise LookupError('No image defined in stack or init')
        else:
            self.image = image
        self.version = version


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
        #state['stage'] = self.stage
        return state

    def deploy_container(self, output=True):
        if docker.image_exists(self.stack.host, self.get_version()):
            docker.pull_image(self.stack.host, self.image, self.version)

        c = docker.create_container(self.stack.host, self)
        self.containerid = c['Id']
        # Handle ports here
        docker.start_container(self.stack.host, c['Id'])
        info = None
        counter = 5
        while not info and counter > 0:
            info = docker.get_container(self.stack.host, self.containerid)
            if output:
                if info:
                    print "Container %s running on %s, port %s" % (self.name,
                                                                   self.stack.host,
                                                                   info['Ports'][0]['PublicPort'])
                else:
                    print "Waiting for container to be listed %s" % (str(counter))
                    sleep(1)

            counter -= 1

        self.port = str(info['Ports'][0]['PublicPort'])

    def remove_container(self):
        if self.containerid:
            id = self.containerid
            docker.stop_container(self.stack.host, id)
        else:
            id = self.name
        docker.stop_container(self.stack.host, id)
        docker.remove_container_byid(self.stack.host, id)

if __name__ == '__main__':
    c = container()
