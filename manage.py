#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Global imports
import argparse
import requests
from sqlalchemy.exc import IntegrityError

# Local imports
import basefunc
from lib import init
from lib import config as cfg
config = cfg.get_config()
rules = cfg.get_rules_config()
cconfig = cfg.get_container_config()


def create_db(args):
    """Initiates based on config"""
    init.init(create=True)


def new_service(args):
    """Process function for deploying service
    Arguments:
        args: name, image, versions, stacks
    """
    service = basefunc.create_service(args.name)
    if not service:
        print "Service not registered"
        return
    # Stacks = 1 if not present as argument
    stacks = args.stacks if args.stacks else 1
    for i in range(0, stacks):
        host = service.choose_host()
        stack = basefunc.create_stack(service, args.image, host)
        try:
            basefunc.create_containers(stack, args.versions)
        except StandardError as e:
            print e


def new_endpoint(args):
    """Creates a new endpoint connected to a service"""
    service = basefunc.get_service(args.service)
    if service:
        try:
            endpoint = basefunc.make_endpoint(service, args.name, args.port, stackpointer=args.stackpointer)
            basefunc.session.commit()
            basefunc.view_endpoint(None, obj=endpoint)
        except IntegrityError as e:
            print "Endpoint not added: %s" % (e.message)
            basefunc.session.rollback()


def connect(args):
    """Connect two or more services together"""
    pobj = []
    cobj = []
    endpoint = basefunc.get_endpoint(args.endpoint)
    service = basefunc.get_service(args.service)

    if endpoint and service:
        # Find all parents and childs
        if args.parent:
            for parent in args.parent:
                pobj.append(basefunc.get_service(parent))
        if args.child:
            for child in args.child:
                cobj.append(basefunc.get_service(child))

        try:
            basefunc.add_relation(endpoint, service, pobj, cobj, args.stackpointer)
        except IntegrityError as e:
            print "Duplicate detected: %s" % e.message
    else:
        print "Endpoint (%s) or service (%s) not found" % (args.endpoint,
                                                           args.service)


def new_version(args):
    """New version of container
    Finds service, pushes new containers
    """
    service = basefunc.get_service(args.service)
    containers = []
    for stack in service.stacks:
        ### CHECK CONSTRAINTS HERE. IN COMPLIANCE WITH VERSIONING?
        print "Pushing new container with version %s on stack %s" % (args.version, stack.name)
        containers.append(basefunc.push_on_stack(stack, args.version))

    for container in containers:
        container.deploy_container()

    basefunc.session.add_all(containers)
    basefunc.session.commit()


def pop(args):
    service = basefunc.get_service(args.service)
    if service:
        if args.single:
            stack = service.stack[0]
            print "Only poping on stack %s" % stack.name
            basefunc.pop(service, stack, position=args.stackpointer)
        else:
            basefunc.pop(service, None, position=args.stackpointer)


def view(args):
    # show all services
    if 'services' in args.type:
        basefunc.view_services()
    # Show one service like name
    elif 'service' in args.type and args.name:
        basefunc.view_service(args.name)
    # Show all endpoints
    elif 'endpoints' in args.type:
        basefunc.view_endpoints()
    # Show one endpoint
    elif 'endpoint' in args.type and args.name:
        basefunc.view_endpoint(args.name)
    elif 'containers' in args.type:
        basefunc.view_containers()
    elif 'stack' in args.type and args.name:
        service = basefunc.get_service(args.name)
        basefunc.view_stack(service)


def delete(args):
    if 'containers' in args.type:
        basefunc.remove_all_containers()
    else:
        print "Not running. Argument %s not supported" % (args.type)


def deploy(args):
    if 'containers' in args.type:
        basefunc.deploy_all_containers()


def upstream(args):
    """Get the upstream versions of a container"""
    url = "https://registry.hub.docker.com/v1/repositories/%s/tags"
    service = basefunc.get_service(args.service)
    if service:
        if service.stacks:
            r = requests.get(url % service.stacks[0].image)
            # THIS IS REALLY INSECURE! Need a fast implementation :)
            tags = eval(r.text)
            for tag in tags:
                print "Tag: %s, layer: %s" % (tag['name'], tag['layer'])
        else:
            print "Docker image not defined"
    else:
        print "Service not found"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Service management tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparser = parser.add_subparsers()
    # When init is sendt
    parser_init = subparser.add_parser('init', description='Initiates database')
    parser_init.set_defaults(func=create_db)

    # Parsing for show command
    parser_view = subparser.add_parser('show', description='Show the different items')
    parser_view.add_argument('type', type=str,
                             help='Different types of items to show',
                             choices=['services', 'service', 'endpoints',
                            'endpoint', 'stacks', 'stack', 'containers'])
    parser_view.add_argument('name', type=str, nargs='?',
                             help='Name of service. Use percent to search')
    parser_view.set_defaults(func=view)

    # Parser for the addservice command
    parser_add_service = subparser.add_parser('addservice',
                                              description="Add new service")
    parser_add_service.add_argument('name', type=str, help='Name of service')
    parser_add_service.add_argument('-i', '--image', type=str,
                                    help='Docker image path for pull')
    parser_add_service.add_argument('-s', '--stacks', type=int, default=1,
                                    help='Number of stacks to add')
    parser_add_service.add_argument('-v', '--versions', nargs='+', type=str,
                                    help='Version(s) to add')
    parser_add_service.set_defaults(func=new_service)

    parser_add_endpoint = subparser.add_parser('addendpoint',
                                    description='Add a new endpoint to service')
    parser_add_endpoint.add_argument('-s', '--service', type=str, required=True,
                                     help='Name of the main service', )
    parser_add_endpoint.add_argument('name', type=str, help='Name of endpoint')
    parser_add_endpoint.add_argument('-p', '--port', help='Public port')
    parser_add_endpoint.add_argument('-stack', '--stackpointer', type=int, default=0,
                                     help='Default stack pointer for tree')
    parser_add_endpoint.set_defaults(func=new_endpoint)

    parser_connect = subparser.add_parser('connect',
                                          description='Connect services')
    parser_connect.add_argument('service', type=str, help='Service to connect')
    parser_connect.add_argument('-p', '--parent', nargs='+', type=str,
                                help='Parent service')
    parser_connect.add_argument('-c', '--child', nargs='+', type=str,
                                help='Childe service')
    parser_connect.add_argument('-e', '--endpoint', type=str,
                                help='Endpoint')
    parser_connect.add_argument('-stp', '--stackpointer', type=int,
                                help='Optional stack pointer')
    parser_connect.set_defaults(func=connect)


    parser_do_release = subparser.add_parser('release',
                                             description='Do a service release')
    parser_do_release.add_argument('service', type=str,
                                   help='Service to do release on')
    parser_do_release.add_argument('-v', '--version', type=str, required=True,
                                   help='Version of the new container')
    parser_do_release.set_defaults(func=new_version)

    parser_pop = subparser.add_parser('pop',
                                      description='Pop container from service')
    parser_pop.add_argument('service', type=str,
                            help='Service to pop container from')
    parser_pop.add_argument('-stp', '--stackpointer', type=int, default=0,
                            help='Which container to pop')
    parser_pop.add_argument('-s', '--single', default=False, action='store_false',
                            help='Remove from one stacks')
    parser_pop.set_defaults(func=pop)

    parser_delete = subparser.add_parser('delete', description='Delete')
    parser_delete.add_argument('type', type=str, choices=['containers',
                                                          'services', 'stacks'])
    parser_delete.add_argument('-n', '--name', type=str,
                               help='Name of item to remove')
    parser_delete.set_defaults(func=delete)

    parser_deploy = subparser.add_parser('deploy', description='Deploy')
    parser_deploy.add_argument('type', type=str, choices=['containers'])
    parser_deploy.add_argument('-n', '--name', type=str,
                               help='Name of item to deploy')
    parser_deploy.set_defaults(func=deploy)

    parser_upversions = subparser.add_parser('upstream',
                                             description='Find upstream versions')
    parser_upversions.add_argument('service', type=str,
                                   help='The version to check versions on')
    parser_upversions.set_defaults(func=upstream)

    args = parser.parse_args()
    args.func(args)
