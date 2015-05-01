#!/usr/bin/env python
# -*- coding: utf-8 -*-

from docker import Client
from requests import ConnectionError

connections = {}


def connect(host='localhost', base_url='unix://var/run/docker.sock', tls=False):
    if host not in connections.keys():
        try:
            c = Client(base_url=base_url, tls=tls)
            connections[host] = c
        except ConnectionError:
            return None
    else:
        return connections[host]
    return c


def get_containers(host):
    """Returns the docker containers
    Arguments:
        host: hostname of host
    """
    return connections[host].containers()


def pull_image(host, image, version):
    """Pulls the image and version to the host
    Arguments:
        host: hostname of host
        image: image name
        version: image version
    returns the status
    """
    status = connections[host].pull('%s:%s' % (image, version))
    return status


def create_container(host, container):
    """Create a container (needs to be started)
    Arguments:
        host: hostname of host to start on
        container: container object
    """
    # hostname, volumes, detached, ports=[1234,134]
    # image: 'name:tag'
    c = connections[host].create_container(image=container.image,
                                           command=container.cmd,
                                           name=container.name)
    return c


def start_container(host, idorname):
    """Start existing container
    Arguments:
        host: hostname the container is on
        idorname: container identifyer
    """
    # port_bindings={1111: ('127.0.0.1', 4567)},
    response = connections[host].start(container=idorname,
                                       # publish_all_ports=False,
                                       restart_policy={'Name': 'always'}
                                       )
    return response


def remove_container(host, container):
    """Removes a container from a host
    Arguments:
        host: host to remove container from
        container: container object to remove
    """
    return connections[host].remove_container(container=container.name,
                                              force=True)
