#!/usr/bin/env python
# -*- coding: utf-8 -*-

from docker import Client
from requests import ConnectionError
import config as cfg

config = cfg.get_config()
cconfig = cfg.get_container_config()

connections = {}

hostnames = cconfig.get('main', 'hostnames').split(',')
hosts = cconfig.get('main', 'hosts').split(',')
port = cconfig.get('main', 'port')


def connect(host='localhost', base_url='unix://var/run/docker.sock', tls=False):
    if host not in connections.keys():
        try:
            c = Client(base_url=base_url, tls=tls)
            connections[host] = c
        except ConnectionError:
            return None


def get_containers(host):
    """Returns the docker containers
    Arguments:
        host: hostname of host
    """
    return connections[host].containers()


def get_container(host, containerid):
    """Get info about a specifc container
    Arguments:
        hostname
        containerid: hash identifier
    """
    containers = get_containers(host)
    for container in containers:
        if containerid in container['Id']:
            return container


def pull_image(host, image, version):
    """Pulls the image and version to the host
    Arguments:
        host: hostname of host
        image: image name
        version: image version
    returns the status {'status','progressDetail', 'id'}
    """
    status = connections[host].pull('%s:%s' % (image, version))
    return status


def create_container(host, container):
    """Create a container (needs to be started)
    Arguments:
        host: hostname of host to start on
        container: container object
    Returns:
        dict: {Id: hash, Warnings: None}
    """
    # hostname, volumes, detached, ports=[1234,134]
    # image: 'name:tag'
    c = connections[host].create_container(image=container.get_version(),
                                           #command=container.cmd,
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
                                       publish_all_ports=True,
                                       restart_policy={'Name': 'always'}
                                       )
    return response


def remove_container(host, name):
    """Removes a container from a host
    Arguments:
        host: host to remove container from
        container: container object to remove
    """
    return connections[host].remove_container(container=name,
                                              force=True)


def image_exists(host, imagetag):
    """Checks if image is on host
    Arguments:
        host: hostname
        imagetag: name and optional tag of image
    Returns:
        true: image exists
        false: does not exist
    """
    images = connections[host].images()
    for image in images:
        if imagetag in image['RepoTags']:
            return True
    return False


def container_exists(host, name, all=False):
    """Check if a container with the same name is running on the host
    """
    for container in connections[host].containers(all=all):
        if name in container['Names']:
            return True
    return False


def stop_container(host, id):
    """Stop container"""
    connections[host].stop(resource_id=id, timeout=1)


def remove_container_byid(host, id):
    """Remove container"""
    connections[host].remove_container(id)


def init():
    for i in range(0,len(hostnames)):
        connect(host=hostnames[i], base_url='http://%s:%s' % (hosts[i], str(port)))

init()
