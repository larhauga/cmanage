#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script for defining base functions
from sqlalchemy.exc import IntegrityError
from terminaltables import AsciiTable
from exceptions import NotImplementedError

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
def create_service(name):
    """Creates a new service
    Arguments:
        name: Name of the new service
    Constraints:
        name: unique
    """
    # HERE NEEDS CHECK OF STATE
    if not session.query(Service).filter(Service.name == name).first():
        try:
            s = Service(name)
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

def view_service(name):
    """Prints out information about one service based on its name"""
    view_services(filterquery=session.query(Service).filter(Service.name == name))

def view_services(filterquery=None):
    """Prints out list of services and its relevant information"""
    table = []
    table.append(["Service Name", "Stacks", "Containers", "Parent S", "Child S", "Endpoints" ])
    if filterquery:
        services = filterquery.all()
        #services = session.query(filterquery).all()
    else:
        services = session.query(Service).all()

    for service in services:
        state = service.get_state()
        parents = [p['parent'] for p in state['parent']]
        children = [c['child'] for c in state['childs']]
        table.append([str(state['name']),
                      "\n".join([ s['name'] for s in state['stacks'] if s]),
                      str(sum([len(x['container']) for x in state['stacks']])),
                      "\n".join(parents),
                      "\n".join(children),
                      "\n".join(state['endpoints'])])
    t = AsciiTable(table)
    t.inner_row_border = True
    print t.table


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
    session.add(stack)
    session.commit()
    return stack

def update_stack(service):
    """Update stack for service
    Dont know what this will do yet.
    Intended to add one container version on a stack...
    """
    raise NotImplementedError()

def view_stack(service, stackname=None):
    """View the stack container version and position and tree points
    Arguments:
        service: service object
        stackname: Name of stack if only one stack should be viewed
    """
    table_data = [['Stackname', 'host', 'image', 'conatiners']]
    for stack in service.stacks:
        table_data.append([str(stack.name), str(stack.host), str(stack.image), "\n".join([c.name for c in stack.container])])

    print table_data
    table = AsciiTable(table_data)
    table.inner_row_border = True
    print table.table


# Endpoint functions
def make_endpoint(service, name, publicport, stackpointer=None):
    """Create and connect a endpoint to a service
    Arguments:
        name: additional name: "service-endpoint-%s"
        service: service object
        publicport: public port
        stackpointer: default place on stack
    Constraints:
    """
    e = Endpoint(name, service, publicport, stackpointer)
    return e

def view_endpoint(endpointname):
    """Prints out a single endpoint"""
    table_data = [['Endpoint name', 'ip', 'pubport', 'url', 'mainservice', 'tree']]
    endpoint = session.query(Endpoint).filter(Endpoint.name == endpointname).first()
    subtree = view_endpoint_tree(endpoint)
    table_data.append([str(endpoint.name), str(endpoint.ip), str(endpoint.pubport), str(endpoint.url), str(endpoint.service.name), subtree])
    tree = AsciiTable(table_data)
    tree.inner_row_border = True
    print tree.table

def view_endpoint_tree(endpoint):
    subtree_data = [['parent', 'child', 'stackposition']]
    for tree in endpoint.service_tree:
        state = tree.get_state()
        subtree_data.append([str(state['parent']), str(state['child']), str(state['stackpos'])])
    subtree = AsciiTable(subtree_data)
    return subtree.table


def view_endpoints():
    """Lists the endpoints defined
    Arguments:
        *sort by service
        *sort by stage
    """
    table_data = [['Endpoint name', 'ip', 'pubport', 'url', 'mainservice', 'tree']]
    for endpoint in session.query(Endpoint).all():
        subtree = view_endpoint_tree(endpoint)
        table_data.append([str(endpoint.name), str(endpoint.ip), str(endpoint.pubport), str(endpoint.url), str(endpoint.service.name), subtree])
    table = AsciiTable(table_data)
    table.inner_row_border = True
    print table.table


# Container functions
def push_on_stack(stack, version):
    """Push new version of a container on stack
    Arguments:
        stack: stack object
        version: new version of image
    Returns:
        the new container
    """
    # Container(stack, version, image=None, name='app')
    c = Container(stack, version)
    return c

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

def replace(service, position, direction, stack=None):
    """Replaces a container on a stack, with neighbour
    Arguments:
        service: service object
        position: position of stack to replace
        direction: which of the surrounding containers to copy
    kwargs:
        stack: name of stack, if only one stack
    """
    raise NotImplementedError()
    if stack:
        pass


# Tree operations
def create_tree(relations):
    raise NotImplementedError()


def view_tree(service):
    """Shows a tree"""
    raise NotImplementedError()


# State
def get_state():
    """Gets the state of the complete environment"""
    state = {}
    for service in session.query(Service).all():
        state[service.name] = service.get_state()
    return state

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
    view_service('webapp1')
    #view_services()
    #s = get_service('WebFront')
    #view_stack(s)

    #view_endpoint('alabi')
    #view_endpoints()
    #s = create_service('WebFront', 20202)
    #print s
    #print s.name
