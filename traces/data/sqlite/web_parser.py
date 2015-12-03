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

import utils_cocoa
import config as cfg

import sqlite3

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from models import Tab

"""
This file should scrape Chrome and Safari web histories from their respective
databases. We can access the Safari database, but the Chrome database is locked
whenever chrome is open. We need to find a work around, possibly opening in
read-only? It looks like you can do read-only in python 3.4.0, but not 2.7:
http://stackoverflow.com/questions/10205744/opening-sqlite3-database-from-python-in-read-only-mode

This site includes a possible workaround for Python 2.7
    fd = os.open(filename, os.O_RDONLY)
    c = sqlite3.connect('/dev/fd/%d' % fd)
    os.close(fd)

This sometimes seems to work for me, but not consistently.
"""

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
    conn.close()

def update_safari_urls(start_time, end_time):
    start = utils_cocoa.unix_to_safari(start_time)
    end = utils_cocoa.unix_to_safari(end_time)

    filename = os.path.expanduser('~/Library/Safari/History.db')
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    #TODO add a sql left join here to get url data
    v = c.execute("SELECT * FROM history_visits where visit_time BETWEEN %d and %d" % (start, end))
    print v.fetchall()
    conn.close()

def update_chrome_urls(start_time, end_time):
    # open the database in read-only mode
    # http://stackoverflow.com/questions/10205744/opening-sqlite3-database-from-python-in-read-only-mode
    start = utils_cocoa.unix_to_chrome(start_time)
    end = utils_cocoa.unix_to_chrome(end_time)

    filename = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/History')
    fd = os.open(filename, os.O_RDONLY)
    conn = sqlite3.connect('/dev/fd/%d' % fd)

    c = conn.cursor()
    c.execute("SELECT * FROM visits WHERE visit_time BETWEEN " + str(start) +" AND " + str(end))
    print c.fetchall()
    os.close(fd)

    # get datetimes that we want to query

def parse_tabs(session):
  # get name of file to read
  tabfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.TABLOG)

  # read the file, write lines to database, and save lines that were not
  # written to the database
  # TODO may need to check if file is already open using a file lock
  if os.path.isfile(tabfile):
      f = open(tabfile, 'r+')
      lines_to_save = []
      for line in f:
          try:
              text = ast.literal_eval(line.rstrip())
              tab = Tab(text['time'], text['title'], text['url'], text['event'])
              session.add(tab)
          except:
              print "Could not save " + str(line) + " to the database. Saving for the next round of parsing."
              lines_to_save.append(line)
      # write lines that did not make it into the database to the start of the
      # file and delete the rest of the file
      f.seek(0)
      for line in lines_to_save:
          f.write(line)
      f.truncate()
      f.close()
