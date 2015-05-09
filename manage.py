#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from sqlalchemy.exc import IntegrityError

#from lib import init
import basefunc
from lib import init
from lib import config as cfg
config = cfg.get_config()
rules = cfg.get_rules_config()

def create_db(args):
    init.init(create=True)

def new_service(args): #name, image, versions, nrstacks=1):
    """Process function for deploying service
    Arguments:
        args: name, image, versions, stacks
            #name: The name of the service
            #image: Docker image (repo)
            #versions: list of versions or one version ['version']
            stacks: number of stacks
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


def view(args):
    #if 'help' in args.name:
        #print "Show {all, service(s), endpoint(s), stack(s), tree(service)}"
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
    #elif 'stacks' in args.type:
        #basefunc.view_stack
    elif 'containers' in args.type:
        basefunc.view_containers()
    elif 'stack' in args.type and args.name:
        service = basefunc.get_service(args.name)
        basefunc.view_stack(service)

def delete(args):
    if 'containers' in args.type:
        basefunc.remove_all_containers()

def main(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Service management tool',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    subparser = parser.add_subparsers()
    parser_init = subparser.add_parser('init', description='Setup program for first time use')
    parser_init.set_defaults(func=create_db)
    # Parser for the view command
    parser_view = subparser.add_parser('show', description='Show the different items')
    parser_view.add_argument('type', type=str, choices=['services', 'service',
                                                       'endpoints', 'endpoint',
                                                       'stacks', 'stack',
                                                        'containers'],
                             help='Different types of items to show')
    parser_view.add_argument('-n', '--name', type=str,
                             help='Name of service. Use percent to search')
    parser_view.set_defaults(func=view)

    # Parser for the addservice command
    parser_add_service = subparser.add_parser('addservice', description="Add new service")
    parser_add_service.add_argument('name', type=str, help='Name of service')
    parser_add_service.add_argument('-i', '--image', type=str, help='Docker image path for pull')
    parser_add_service.add_argument('-s', '--stacks', type=int, default=1, help='Number of stacks to add')
    parser_add_service.add_argument('-v', '--versions', nargs='+', type=str, help='Version(s) to add')
    parser_add_service.set_defaults(func=new_service)

    parser_add_endpoint = subparser.add_parser('addendpoint', description='Add a new endpoint to service')
    parser_add_endpoint.add_argument('-s', '--service', type=str, help='Name of the main service', required=True)
    parser_add_endpoint.add_argument('name', type=str, help='Name of endpoint')
    parser_add_endpoint.add_argument('-p', '--port', help='Public port')
    parser_add_endpoint.add_argument('-stack', '--stackpointer', type=int, default=0,
                                     help='Default stack pointer for tree')
    parser_add_endpoint.set_defaults(func=new_endpoint)

    parser_delete = subparser.add_parser('delete', description='Delete')
    parser_delete.add_argument('type', type=str, choices=['containers', 'services', 'stacks'])
    parser_delete.add_argument('-n', '--name', type=str,
                               help='Name of item to remove')
    parser_delete.set_defaults(func=delete)

    #subsubadd.add_argument('name', type=str, help='Name of endpoint')
    #subsubadd.add_argument('--port', type=int, help='Public port of endpoint')
    #subsubadd.add_argument('--defaultpointer', type=int, help='Pointer on stack')
    #image, versions, nrstacks

    # Parameters needed for new service
    #parser.add_argument('--pubport', type=int, help='Port of an endpoint')
    #parser.add_argument('--stacks', type=int, default=1, help='Number of stacks a service should have')

    # Extra parameters for push on stack
    #parser.add_argument('-v', '--version', type=str,
                        #help='Versions of new containers. If containers > 1, this must be a list')

    args = parser.parse_args()
    args.func(args)

    main(args)
