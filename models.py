# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from sqlalchemy import Column, INTEGER, FLOAT, CHAR, TEXT, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GeoInfos(Base):
    __tablename__ = 'geoinfos'

    place_id = Column(String(40), primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    city = Column(String(20), nullable=False)
    address = Column(String(100), nullable=True)
    lng = Column(FLOAT, nullable=False)
    lat = Column(FLOAT, nullable=False)


class Ratings(Base):
    __tablename__ = 'ratings'

    place_id = Column(String(40), primary_key=True, nullable=False)
    gg_reviews = Column(INTEGER, nullable=True)
    gg_ratings = Column(FLOAT, nullable=True)
    ta_reviews = Column(INTEGER, nullable=True)
    ta_ratings = Column(FLOAT, nullable=True)


class Types(Base):
    __tablename__ = 'types'

    index = Column(INTEGER, nullable=False, primary_key=True, autoincrement=True)
    place_id = Column(String(40), nullable=False)
    types = Column(String(40), nullable=False)


class Users(Base):
    __tablename__ = 'users'

    index = Column(INTEGER, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(String(20), nullable=False)
    place_id = Column(String(40), nullable=False)