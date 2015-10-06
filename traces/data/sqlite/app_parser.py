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

import config as cfg

from modesl import (App, Window, Geometry)


def parse_apps(session):
    # get names of files to read and mongodb collection to write
    appfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.APPLOG)
    app_collection = db[cfg.APPCOL]

    # read the file, write lines to database, and save lines that were not
    # written to the database
    # TODO may need to check if file is already open using a file lock
    if os.path.isfile(appfile):
        f = open(appfile, 'r+')
        lines_to_save = []
        for line in f:
            try:
                text = ast.literal_eval(line.rstrip())
                app_collection.insert_one(text)
            except:
                print "Could not save " + str(text) + " to the database. Saving for the next round of parsing."
                lines_to_save.append(text)
        # write lines that did not make it into the database to the start of the
        # file and delete the rest of the file
        f.seek(0)
        for line in lines_to_save:
            f.write(line)
        f.truncate()
        f.close()

def parse_windows(session):
    # get names of files to read and mongodb collection to write
    windowfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.WINDOWLOG)
    window_collection = db[cfg.WINDOWCOL]

    # read the file, write lines to database, and save lines that were not
    # written to the database
    # TODO may need to check if file is already open using a file lock
    if os.path.isfile(windowfile):
        f = open(windowfile, 'r+')
        lines_to_save = []
        for line in f:
            try:
                text = ast.literal_eval(line.rstrip())
                window_collection.insert_one(text)
            except:
                print "Could not save " + str(text) + " to the database. Saving for the next round of parsing."
                lines_to_save.append(text)
        # write lines that did not make it into the database to the start of the
        # file and delete the rest of the file
        f.seek(0)
        for line in lines_to_save:
            f.write(line)
        f.truncate()
        f.close()

def parse_geometries(session):
    # get names of files to read and mongodb collection to write
    geofile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.GEOLOG)
    geo_collection = db[cfg.GEOCOL]

    # read the file, write lines to database, and save lines that were not
    # written to the database
    # TODO may need to check if file is already open using a file lock
    if os.path.isfile(geofile):
        f = open(geofile, 'r+')
        lines_to_save = []
        for line in f:
            try:
                text = ast.literal_eval(line.rstrip())
                geo_collection.insert_one(text)
            except:
                print "Could not save " + str(text) + " to the database. Saving for the next round of parsing."
                lines_to_save.append(text)
        # write lines that did not make it into the database to the start of the
        # file and delete the rest of the file
        f.seek(0)
        for line in lines_to_save:
            f.write(line)
        f.truncate()
        f.close()
