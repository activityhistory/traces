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

from models import (App, AppEvent, Window, WindowEvent, Geometry)


def parse_apps(session, activity_tracker):
    #TODO see if there is a way to query the database only for a list of app names
    # get a copy of the starting database so we don't have to query it all the time
    apps = session.query(App).all()
    app_names = []
    for a in apps:
        app_names.append(a.name)

    # read the file, write new apps and events to the database
    appfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.APPLOG)
    if os.path.isfile(appfile):
        f = open(appfile, 'r+')
        lines_to_save = []

        for line in f:
            try:
                # get data from the line of text
                text = ast.literal_eval(line.rstrip())
                t = text['time']
                event = text['type']
                app_name = text['app']
                pid = None

                # get pid of app from database, add app to database if not already there
                if app_name not in app_names:
                    # add app to the database
                    app_to_add = App(t, app_name)
                    session.add(app_to_add)
                    activity_tracker.storage.sqlcommit()

                    # update our local app list
                    apps = session.query(App).all()
                    app_names = []
                    for a in apps:
                        app_names.append(a.name)

                pid = app_names.index(app_name) + 1 # array starts at 0, database ids a 1

                # add the app event to the database
                ae = AppEvent(t, pid, event)
                session.add(ae)

            except:
                raise
                print "Could not save " + str(text) + " to the database. Saving for the next round of parsing."
                lines_to_save.append(text)
        # write lines that did not make it into the database to the start of the
        # file and delete the rest of the file
        f.seek(0)
        for line in lines_to_save:
            f.write(line)
        f.truncate()
        f.close()

#TODO cast text to unicode!
def parse_windows(session, activity_tracker):
    # get a copy of the starting app database so we don't have to query it all the time
    apps = session.query(App).all()
    app_names = []
    for a in apps:
        app_names.append(a.name)

    # get a copy of the starting window database so we don't have to query it all the time
    windows = session.query(Window).all()
    window_names = []
    for w in windows:
        window_names.append(w.name)

    # read the file, write lines to database, and save lines that were not
    # written to the database
    windowfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.WINDOWLOG)
    if os.path.isfile(windowfile):
        f = open(windowfile, 'r+')
        lines_to_save = []
        for line in f:
            try:
                text = ast.literal_eval(line.rstrip())
                t = text['time']
                event = text['type']
                app_name = text['app']
                try:
                    window = text['window']
                except:
                    window = None

                if app_name not in app_names:
                    # add app to the database
                    app_to_add = App(t, app_name)
                    session.add(app_to_add)
                    activity_tracker.storage.sqlcommit()

                    # update our local app list
                    apps = session.query(App).all()
                    app_names = []
                    for a in apps:
                        app_names.append(a.name)

                pid = app_names.index(app_name) + 1 # array starts at 0, database ids a 1

                if window not in window_names:
                    # add app to the database
                    app_to_add = Window(t, pid, window)
                    session.add(app_to_add)
                    activity_tracker.storage.sqlcommit()

                    # update our local app list
                    windows = session.query(Window).all()
                    window_names = []
                    for w in windows:
                        window_names.append(w.name)

                wid = window_names.index(app_name) + 1 # array starts at 0, database ids a 1

                # add the app event to the database
                we = WindowEvent(t, wid, event)
                session.add(we)

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
