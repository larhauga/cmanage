#!/usr/bin/env python
# -*- coding: utf-8 -*-


class service(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self): return self._name

    @name.setter
    def name(self, name): self._name = name


if __name__ == '__main__':
    s = service("hest")
    print type(s)
    s.name = "Hest"
    print s.name
