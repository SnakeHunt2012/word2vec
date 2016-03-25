#!/usr/bin/env python
# -*- coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Word(Base):

    __tablename__ = "word"

    id = Column(Integer, primary_key = True)
    context = Column(String)
    vector = Column(String)

class Bidword(Base):

    __tablename__ = "bidword"

    id = Column(Integer, primary_key = True)
    context = Column(String)
    vector = Column(String)

class Query(Base):

    __tablename__ = "query"

    id = Column(Integer, primary_key = True)
    context = Column(String)
    vector = Column(String)

def connect_database():

    engine = create_engine("postgresql://huangjingwen@localhost/relevence")
    session_maker = sessionmaker()
    session_maker.configure(bind = engine)
    return engine, session_maker()

