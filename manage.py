#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

#from lib import init
import basefunc

def deploy_service(name, image, nrstacks=1):
    service = basefunc.create_service(name)
    host = None
    for i in range(0,nrstacks):
        basefunc.create_stack(service, image, host)


def view(args):
    if 'services' in args:
        basefunc.view_services()
    elif 'endpoints' in args:
        basefunc.view_endpoints()

def main(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Service management tool')
    #parser_show = parser.add_mutually_exclusive_group()
    #parser_create= parser.add_mutually_exclusive_group()

    parser.add_argument('--show', type=view, choices=['endpoints', 'services'], help='Show all services')
    #parser.add_argument('endpoints', type=view, help='Show all services')
    #parser_show.add_argument('endpoints', action=basefunc.view_endpoints, help='Show all endpoints')

    #parser_create.add_argument('hest', help='Makes the horse horse')

    args = parser.parse_args()
    print args

    main(args)
