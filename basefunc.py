#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script for defining base functions
from sqlalchemy.exc import IntegrityError
from terminaltables import AsciiTable
from exceptions import NotImplementedError, StandardError

from lib import config as cfg
from lib import init

from lib.service import Service, Service_tree
from lib.stack import Stack
#from lib.tree import Tree
from lib.container import Container
from lib.endpoint import Endpoint
#from lib.stage import Stage
from docker.errors import APIError
import lib.lib_docker as docker

config = cfg.get_config()
logging = cfg.get_logger()
rules = cfg.get_rules_config()

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
    # check if service exists (name)

    if not session.query(Service).filter(Service.name == name).first():
        try:
            s = Service(name)
            session.add(s)
            session.commit()
        except IntegrityError as e:
            print('Port allready in use: %s' % str(e.orig))
            return None
    else:
        print('Service already exists')
        return None
    return s

def get_service(name):
    """Searches after the service name"""
    return session.query(Service).filter(Service.name == name).first()

def view_service(name):
    """Prints out information about one service based on its name"""
    view_services(filterquery=session.query(Service).filter(Service.name.like(name)))

def view_services(filterquery=None):
    """Prints out list of services and its relevant information"""
    table = []
    table.append(["Service Name", "Stacks", "Containers", "Parent S", "Child S", "Endpoints" ])
    if filterquery:
        services = filterquery.all()
        #services = session.query(filterquery).all()
    else:
        services = session.query(Service).all()
    if not services:
        print "No services met the search"
        return

    for service in services:
        state = service.get_state()
        parents = [p['parent'] for p in state['parent']]
        children = [c['child'] for c in state['childs']]
        cs = []
        for stack in state['stacks']:
            for i, container in enumerate(stack['container']):
                endpoint = service.tree_on_stack_pointer(i)
                if endpoint:
                    cs.append("%s:%s:%s" % (container['name'], container['version'], endpoint.name))
                else:
                    cs.append("%s:%s" % (container['name'], container['version']))
            #cs.extend(["%s:%s" % (c['name'],c['version']) for c in stack['container']])
        table.append([str(state['name']),
                      "\n".join([ s['name'] for s in state['stacks'] if s]),
                      str("\n".join(cs)),
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

def get_endpoint(name):
    """Finds an endpoint based on name"""
    return session.query(Endpoint).filter(Endpoint.name.like(name)).first()

def view_endpoint(endpointname, obj=None):
    """Prints out a single endpoint"""
    table_data = [['Endpoint name', 'ip', 'pubport', 'url', 'mainservice', 'stackpointer', 'tree']]
    if not obj:
        endpoint = session.query(Endpoint).filter(Endpoint.name.like(endpointname)).first()
    else:
        endpoint = obj
    if endpoint:
        print endpoint.get_state()
        subtree = view_endpoint_tree(endpoint)
        table_data.append([str(endpoint.name), str(endpoint.ip), str(endpoint.pubport), str(endpoint.url), str(endpoint.service.name), str(endpoint.stackpointer), subtree])
        tree = AsciiTable(table_data)
        tree.inner_row_border = True
        print tree.table
    else:
        print "Endpoint not found"

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
    table_data = [['Endpoint name', 'ip', 'pubport', 'url', 'mainservice', 'stackpointer', 'tree']]
    for endpoint in session.query(Endpoint).all():
        subtree = view_endpoint_tree(endpoint)
        table_data.append([str(endpoint.name), str(endpoint.ip), str(endpoint.pubport), str(endpoint.url), str(endpoint.service.name), str(endpoint.stackpointer), subtree])
    table = AsciiTable(table_data)
    table.inner_row_border = True
    print table.table


def switch_stackpointer(endpoint, service, newpointer):
    """Switch the pointer of an endpoint"""
    tree = session.query(Service_tree).filter(Service_tree.child == service,
                                            Service_tree.endpoint == endpoint).first()
    tree.stackpos = newpointer
    session.commit()

# Container functions
def create_containers(stack, versions):
    """Initial function that creates containers
    Enforces the state rules"""
    containers = []
    if not check_versions(stack, versions):
        pass
    if type(versions) == list:
        if len(versions) < rules.getint('stack', 'min_containers'):
            diff = rules.getint('stack', 'min_containers') - len(versions)
            # Pushes the different versions on the stack
            for version in versions:
                containers.append(push_on_stack(stack, version))
            # Padds with N versions to fill up stack according to constraint
            for i in range(0, diff):
                containers.append(push_on_stack(stack, versions[-1]))
        else:
            for version in versions:
                containers.append(push_on_stack(stack, version))
    else:
        for i in range(0, rules.getint('stack', 'min_containers')):
            containers.append(push_on_stack(stack, versions))

    # Check if image exists on host
    for container in containers:
        if not docker.image_exists(container.stack.host, container.get_version()):
            response = docker.pull_image(stack.host, stack.image, container.version)
            if 'not found' in response:
                print "Image not found. Rolling back containers"
                session.rollback()
                raise StandardError('Image not found. Reverting')
            else:
                print "Image %s:%s downloaded on %s" % (stack.image, container.version, stack.host)

    for container in containers:
        session.add(container)

    session.commit()

    for container in containers:
        container.deploy_container()
    session.commit()



def check_versions(stack, versions):
    existing = stack.get_versions()
    vconf = rules.get('stack', 'versions').split(',')
    if type(versions) == list:
        v = existing + versions
    else:
        v = existing + [versions]

    ok = False
    for i,ver in enumerate(v):
        if not i == 0:
            if 'incremental' in vconf and 'equal' in vconf:
                if 'latest' in ver:
                    ok = True
                elif ver > v[i-1]:
                    ok = True
                elif ver >= v[i-1]:
                    ok = True
                else:
                    ok = False
            elif 'incremental' in vconf and not ver > v[i-1]:
                return False
            elif 'equal' in vconf and not ver == v[i-1]:
                return False
            elif 'all':
                return True
    return ok
    #return True

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
    if not stack:
        for stack in service.stacks:
            if len(stack.container) <= rules.getint('stack','min_containers'):
                raise StandardError('Not enough containers on stack. Poping not compliant with rules')
    else:
        if len(stack.container) <= rules.getint('stack', 'min_containers'):
            raise StandardError('Not enough containers on specified stack. Not compliant to pop')
    # HERE NEEDS CONSTRAINTS CHECKING
    # HERE NEEDS HAPROXY INTEGRATION

    if not stack:
        for s in service.stacks:
            c = s.containers.pop(position)
            # HERE NEEDS DOCKER/HAPROXY
            c.remove_container()
            session.delete(c)
    else:
        c = stack.container[position]
        c.remove_container()
        session.delete(c)

    session.commit()

def replace(service, position, direction, stack=None):
    """Replaces a container on a stack, with neighbour
    Arguments:
        service: service object
        position: position of stack to replace (arraypos 0-n)
        direction: which of the surrounding containers to copy
    kwargs:
        stack: name of stack, if only one stack
    """
    raise NotImplementedError()
    # find the new version
    containers = service.stacks[0].containers
    version = containers[position+direction].version
    # Create a new container that is not related to a stack yet
    c = Container(None, version, image=service.stacks[0].image)
    #for stack in service.stacks:
        ## find the version
    #if stack:
        ##pass

def view_containers():
    services = session.query(Service).all()
    containers = []
    table = []
    table.append(['Name', 'image', 'version', 'port', 'containerid'])
    for service in services:
        for stack in service.stacks:
            for container in stack.container:
                st = container.get_state()
                table.append([str(st['name']), str(st['image']), str(st['version']), str(st['port']), str(st['containerid'])[0:15]])

    t = AsciiTable(table)
    t.inner_row_border = True
    print t.table

def remove_all_containers():
    for container in session.query(Container).all():
        try:
            print "Removing container %s from %s" % (container.name, container.stack.host)
            container.remove_container()
        except APIError as e:
            print e.message
            if 'Not Found' in e.message:
                print "Container %s not found on host %s" % (container.name, container.stack.host)
    session.commit()

def deploy_all_containers():
    for container in session.query(Container).all():
        try:
            container.deploy_container()
        except APIError as e:
            if '409 Client Error: Conflict' in e.message:
                print "Container %s allready running on %s" % (container.name, container.stack.host)
            else:
                print "Error on container %s: %s" % (container.name, str(e))
    session.commit()
# Tree operations
def create_tree(endpoint, relations):
    """Create tree from list of named dicts
    Arguments:
        endpoint: object of the endpoint or name
        relations: string or list of dict: {parent, child, stackref}
    """
    e = None
    if endpoint == Endpoint:
        e = endpoint
    else:
        e = session.query(Endpoint).filter(Endpoint.name == endpoint).first()

    if type(relations) == str:
        relations = eval(relations)
    for item in relations:
        tree_node = Service_tree(item['parent'], item['child'], e)
        session.add(tree_node)
    session.commit()

def add_relation(endpoint, service, parents, childs, stackpointer):
    """Create a new relation in a service tree based on service
    Arguments:
        endpoint: Tree to connect to
        service: The service to connect
        parents: the parent services of the service
        childs: the child of the service
        stackpointer: optional stack pointer"""
    # Handle parents
    trees = []
    for parent in parents:
        trees.append(Service_tree(parent, service, endpoint, stackpointer))
    for child in childs:
        trees.append(Service_tree(service, child, endpoint, stackpointer))

    session.add_all(trees)
    session.commit()
    # HAndle childs


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
