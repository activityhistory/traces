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
import sys
import pymongo
import sqlalchemy

import config as cfg

import utils_cocoa
import preferences

import data.sqlite.key_parser as key_parser
import data.sqlite.click_parser as click_parser
import data.sqlite.scroll_parser as scroll_parser
import data.sqlite.move_parser as move_parser
import data.sqlite.app_parser as app_parser
import data.sqlite.recorder_parser as recorder_parser
import data.sqlite.chrome_parser as chrome_parser

import data.sqlite.models as models

from data.sqlite.models import (Click, Keys, Move, Scroll, App, AppEvent, Window,
                    WindowEvent, RecordingEvent, Geometry)


class Storage:
    def __init__(self, activity_tracker):
        self.db_name = os.path.join(cfg.CURRENT_DIR, cfg.SQLDB)
        self.last_commit = cfg.NOW()
        self.activity_tracker = activity_tracker

        # make sql database
        if cfg.STORAGE == "sqlite":
            try:
                self.session_maker = models.initialize(self.db_name)
                self.session = self.session_maker()

            except sqlalchemy.exc.OperationalError:
                # show modal error
                print "Database operational error. Your storage device may be full. Exiting Selfspy..."
                utils_cocoa.show_alert("Database operational error. Your storage device may be full. Exiting Selfspy...")

                # close the program
                sys.exit()

    def parseLogs(self):
        print "parsing logs"
        if (cfg.STORAGE is "mongo"):
            self.parseToMongo()
        else:
            self.parseToSqlite()
            # raise Exception("No database defined")

    def parseToMongo(self):
      # open database server
      client = pymongo.MongoClient()
      db = client[cfg.DB]
      try:
          # parse all the relevant log files
          data.mongo.key_parser.parse_keys(db)
          data.mongo.click_parser.parse_clicks(db)
          data.mongo.scroll_parser.parse_scrolls(db)
          data.mongo.move_parser.parse_moves(db)
          data.mongo.app_parser.parse_apps(db)
          data.mongo.app_parser.parse_windows(db)
          data.mongo.app_parser.parse_geometries(db)
      except:
          print "Had an issue parsing to MongoDB"

    def parseToSqlite(self):
        key_parser.parse_keys(self.session)
        click_parser.parse_clicks(self.session)
        scroll_parser.parse_scrolls(self.session)
        move_parser.parse_moves(self.session)
        recorder_parser.parse_recorder(self.session)
        app_parser.parse_apps(self.session, self.activity_tracker)
        app_parser.parse_windows(self.session, self.activity_tracker)
        app_parser.parse_geometries(self.session, self.activity_tracker)
        chrome_parser.get_first_url()

        self.sqlcommit()

    def sqlcommit(self):
        self.last_commit = cfg.NOW()
        for _ in xrange(1000):
            try:
                self.session.commit()
                break
            except sqlalchemy.exc.OperationalError:
                # pause recording
                if(preferences.getValueForPreference("recording")):
                    self.activity_tracker.sniffer.delegate.toggleLogging_(self)
                self.session.rollback()
                # show modal alert
                print "Database operational error. Your storage device may be full. Turning off Selfspy recording."
                utils_cocoa.show_alert("Database operational error. Your storage device may be full. Turning off Selfspy recording.")
                break
            except:
                raise
                print "Rollback database"
                self.session.rollback()

    # TODO make this os agnostic, and make it work for MongoDB
    # TODO figure out way to pass number of minutes to this method
    def clearData(self):
        # minutes_to_delete = notification.object().clearDataPopup.selectedItem().tag()
        # text = notification.object().clearDataPopup.selectedItem().title()
        #
        # if minutes_to_delete == -1:
        #     delete_from_time = datetime.datetime.min
        # else:
        #     delta = datetime.timedelta(minutes=minutes_to_delete)
        #     now = datetime.datetime.now()
        #     delete_from_time = now - delta
        #
        # # delete data from all tables
        #
        # screenshot_directory = os.path.expanduser(os.path.join(cfg.CURRENT_DIR,"screenshots"))
        # screenshot_files = os.listdir(screenshot_directory)
        #
        # for f in screenshot_files:
        #     if f[0:19] > delete_from_time.strftime("%y%m%d-%H%M%S%f") or  minutes_to_delete == -1 :
        #         os.remove(os.path.join(screenshot_directory,f))

        # print "You asked to delete the last " + text + " of your history"
        pass
