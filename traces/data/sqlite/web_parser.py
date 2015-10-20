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

import sqlite3

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker

"""
This file should scrape Chrome and Safari web histories from their respective
databases. We can access the Safari database, but the Chrome database is locked
whenever chrome is open. We need to find a work around, possibly opening in
read-only? It looks like you can do this in python 3.4.0, but not sure about 2.7
http://stackoverflow.com/questions/10205744/opening-sqlite3-database-from-python-in-read-only-mode
"""

# Possible workaround for Python 2.7
# fd = os.open(filename, os.O_RDONLY)
# c = sqlite3.connect('/dev/fd/%d' % fd)
# os.close(fd)

class Bookmarks(object):
    pass

class URLS(object):
    pass

class Keywords(object):
    pass

class Visits(object):
    pass

class Items(object):
    pass

# These use sqlalchemy to load the database schemas. However, I'm
def loadSafariSession():
    dbPath = os.path.expanduser('~/Library/Safari/History.db')
    engine = create_engine('sqlite:///%s' % dbPath, echo=True)

    metadata = MetaData(engine)
    history_visits = Table('history_visits', metadata, autoload=True)
    mapper(Visits, history_visits)
    history_items = Table('history_items', metadata, autoload=True)
    mapper(Items, history_items)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session

#TODO figure out how to get this to work when database is locked
def loadChromeSession():
    dbPath = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/History')
    engine = create_engine('sqlite:///%s' % dbPath, echo=True)

    metadata = MetaData(engine)
    urls = Table('urls', metadata, autoload=True)
    mapper(URLS, urls)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_first_safari_url():
    conn = sqlite3.connect('/Users/adamrule/Library/Safari/History.db')
    c = conn.cursor()
    c.execute("SELECT * FROM history_items")
    print c.fetchone()
