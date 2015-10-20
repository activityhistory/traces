# -*- coding: utf-8 -*-
"""
Traces: Activity Tracker
Copyright (C) 2015 Adam Rule
with Aurélien Tabard, Jonas Keper, Azeem Ghumman, and Maxime Guyaux

Inspired by Selfspy and Burrito
https://github.com/gurgeh/selfspy
https://github.com/pgbovine/burrito/

You should have received a copy of the GNU General Public License
along with Traces. If not, see <http://www.gnu.org/licenses/>.
"""


import os
import ast

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker

class Bookmarks(object):
    pass

class URLS(object):
    pass

class Keywords(object):
    pass

#----------------------------------------------------------------------
def loadSession():
    """"""
    dbPath = '/Users/adamrule/Library/Application Support/Google/Chrome/Default/History'
    engine = create_engine('sqlite:///%s' % dbPath, echo=True)

    metadata = MetaData(engine)
    urls = Table('urls', metadata, autoload=True)
    mapper(URLS, urls)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_first_url():
    session = loadSession()
    res = session.query(URLS).all()
    print res[1].url

# get_first_url()
