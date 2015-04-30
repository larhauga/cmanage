#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.orm import relationship, backref
#from sqlalchemy.ext.declarative import declarative_base

import base
Base = base.Base

class Stage(Base):
    __tablename__ = 'stage'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    stackpos = Column(Integer, unique=True) # Related to stack position

    def __init__(self, name, stackpos):
        self.name = name
        self.stackpos = stackpos
