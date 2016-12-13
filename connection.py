# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb as mdb
import pandas.io.sql as sql

from sqlalchemy import create_engine
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker

server = 'ec2-54-71-55-133.us-west-2.compute.amazonaws.com'
db_pw = '03171155'
connection_string = 'mysql+mysqldb://root:{}@{}:3306/travel?&charset=utf8'.format(db_pw, server)
engine = create_engine(connection_string, pool_recycle = 3600, encoding='utf-8')
connection = engine.connect()
Session = sessionmaker(bind=engine)