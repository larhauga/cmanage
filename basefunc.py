#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script for defining base functions
from sqlalchemy.exc import IntegrityError
from sys import exit

from lib import config as cfg
from lib import init

from lib.service import Service
from lib.stack import Stack
from lib.tree import Tree
from lib.container import Container
from lib.endpoint import Endpoint
from lib.stage import Stage
import lib.lib_docker as docker

config = cfg.get_config()
logging = cfg.get_logger()

session = init.init()


# Service functions
def create_service(name, port):
    """Creates a new service
    Arguments:
        name: Name of the new service
        port: unique port
    Constraints:
        name: unique
        port: unique
    """
    # HERE NEEDS CHECK OF STATE
    if not session.query(Service).filter(Service.name == name).first():
        try:
            s = Service(name, port)
            session.add(s)
            session.commit()
        except IntegrityError as e:
            print('Port allready in use: %s' % str(e.orig))
            return None
    else:
        return None
    return s

def get_service(name):
    """Searches after the service name"""
    return session.query(Service).filter(Service.name == name).first()

def view_service(service):
    """  """
    pass

def view_services():
    pass

def list_services():
    print "Name, port"
    for service in session.query(Service).all():
        print service.name, service.port


# Stack functions
def create_stack(service, image, host):
    """Creates an empty stack for containers
    Arguments:
        service: service object
        image: base image for container
        host: Where to run stack
    Constraints:
    """
    # HERE NEEDS CONSTRAINTS CHECK
    stack = Stack(service, image, host)
    return stack

def update_stack(service):
    """Update stack for service
    Dont know what this will do yet.
    Intended to add one container version on a stack...
    """
    pass

def view_stack(service):
    """View the stack container version and position and tree points"""
    pass


# Endpoint functions
def make_endpoint(service):
    """Create and connect a endpoint to a service
    Arguments:
        service: service object
    Constraints:
    """
    pass

def view_endpoints():
    """Lists the endpoints defined
    Arguments:
        *sort by service
        *sort by stage
    """
    pass


# Container functions
def push_on_stack(service, stackname, version):
    """Push new version of a container on stack
    Arguments:
        service: service object
        stackname: which stack to update
        version: new version of image
    """
    pass

def pop(service, stack, position=0):
    """Removes a container in the specific position
    Arguments:
        service: service object
        stack: specific stack or None for all stacks
        position: position on stack to pop
    """
    # HERE NEEDS CONSTRAINTS CHECKING
    # HERE NEEDS HAPROXY INTEGRATION

    if not stack:
        for s in service.stacks:
            c = s.containers.pop(position)
            # HERE NEEDS DOCKER/HAPROXY
            del c
    else:
        c = stack.containers.pop(position)
        del c

    session.commit()

def replace(service, stack, position, direction):
    """Replaces a container on a stack, with neighbour
    Arguments:
        service: service object
        stack: name of stack
        position: position of stack to replace
        direction: which of the surrounding containers to copy
    """
    pass

def view_tree(service):
    """Shows a tree"""
    pass


# State
def get_state():
    """Gets the state of the complete environment"""
    pass

def get_service_state(service=None, servicename=None):
    """Gets the state of service and all of its relations"""
    if service:
        return service.get_state()
    elif servicename:
        s = session.query(Service).filter(Service.name == servicename).first()
        return s.get_state()
    else:
        return None

def get_endpoint_state(service=None, endpointname=None):
    """Gets the state of an endpoint"""
    if service:
        return service.endpoint.get_state()
    elif endpointname:
        e = session.query(Endpoint).filter(Endpoint.name == endpointname).first()
        return e.get_state()
    else:
        return None

def get_stack_state(stack=None, stackname=None):
    """Gets the state of a stack"""
    if stack:
        return stack.get_state()
    elif stackname:
        stack = session.query(Stack).filter(Stack.name == stackname).first()
        return stack.get_state()
    else:
        return None

def get_container_state(container=None, containername=None):
    """Gets the state of a container"""
    if container:
        return container.get_state()
    elif containername:
        c = session.query(Container).filter(Container.name == containername).first()
        return c.get_state()
    else:
        return None

if __name__ == '__main__':
    list_services()
    #s = create_service('WebFront', 20202)
    #print s
    #print s.name
