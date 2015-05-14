#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Integration to HAProxy
import basefunc
from lib.service import Service, Service_tree
from lib.endpoint import Endpoint
from haproxy.haproxy import HAproxy
from lib import config as cfg
containerconfig = cfg.get_container_config()
containerhostnames = containerconfig.get('main', 'hostnames').split(',')
containerhosts = containerconfig.get('main', 'hosts').split(',')

hostdict = {}
for i, item in enumerate(containerhostnames):
    hostdict[item] = containerhosts[i]

session = basefunc.session


def build_containerdict(containers):
    containerlist = []
    for c in containers:
        tmpc = c.get_state()
        tmpc['hostip'] = hostdict[c.stack.host]
        containerlist.append(tmpc)
    return containerlist


def build_trees():
    every = {}
    leafs = session.query(Service_tree).all()
    for leaf in leafs:
        every[leaf.child.name] = {'endpoint': leaf.endpoint.name,
                                  'port': leaf.port}
        containers = []
        for stack in leaf.child.stacks:
            containers.append(stack.container[leaf.stackpos])

        every[leaf.child.name]['containers'] = build_containerdict(stack.container)

    return every


def rebuild_hap_config():
    hap = HAproxy()
    tree = build_trees()
    # The new config file is written
    # BUT: Needs a restart + handling of discrepanies
    hap.compile(tree)

if __name__ == '__main__':
    hap = HAproxy()
    tree = build_trees()
    #print tree
    hap.compile(tree)
