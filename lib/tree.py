#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
import base


# This needs a many to many relation between tree and service
# http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#many-to-many

association_table = Table(
    'tree_service_relation', base.Base.metadata,
    Column('tree_id', Integer, ForeignKey('tree.id')),
    Column('service_id', Integer, ForeignKey('service.id'))
)
#class Tree_Service_Relation(base.Base):
    #__tablename__ = 'tree_service_relation'



class Tree(base.Base):
    __tablename__ = 'tree'
    id = Column(Integer, primary_key=True)
    #name = Column(String)
    #service_id = Column(Integer, ForeignKey('service.id'), nullable=False)
    endpoint_id = Column(Integer, ForeignKey('endpoint.id'), nullable=False)
    stage_id = Column(Integer, ForeignKey('stage.id'), nullable=False)
    service = relationship('Service', backref=backref('tree'), secondary=association_table)
    endpoint = relationship('Endpoint', backref=backref('tree'))
    stage = relationship('Stage', backref=backref('tree'))

    def __init__(self, service, stage, endpoint):
        self.service = service
        self.stage = stage
        self.endpoint = endpoint

    def add_connection(self, service):
        self.service.add(service)
        pass

    def remove_service(self, service):
        self.service.remove(service)

if __name__ == '__main__':
    t = Tree()
