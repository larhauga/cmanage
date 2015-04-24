#!/usr/bin/env python
# -*- coding: utf-8 -*-


class endpoint(object):
    def __init__(self, name):
        self._name = name
        self._ip = None
        self._port = None
        self._url = None
        self._service = None

    @property
    def name(self): return self._name

    @name.setter
    def name(self, name): self._name = name

    @property
    def ip(self): return self._ip

    @ip.setter
    def ip(self, ip): self._ip = ip

    @property
    def port(self): return self._port

    @port.setter
    def port(self, port): self._port = port

    @property
    def url(self): return self._url

    @url.setter
    def url(self, url): self._url = url

    @property
    def service(self): return self._service

    @service.setter
    def service(self, service): self._service = service

if __name__ == '__main__':
    e = endpoint("hest")
    print type(e)
    e.name = "Hest"
    print e.name
