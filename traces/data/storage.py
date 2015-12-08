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
import datetime

# import pymongo
import sqlalchemy

import config as cfg

import utils_cocoa
import preferences

import data.sqlite.key_parser as key_parser
import data.sqlite.click_parser as click_parser
import data.sqlite.clip_parser as clip_parser
import data.sqlite.scroll_parser as scroll_parser
import data.sqlite.move_parser as move_parser
import data.sqlite.app_parser as app_parser
import data.sqlite.recorder_parser as recorder_parser
import data.sqlite.web_parser as web_parser

import data.sqlite.models as models
from data.sqlite.models import (Click, Keys, Move, Scroll, App, AppEvent, Window,
                    WindowEvent, RecordingEvent, Geometry, Clipboard, Arrangement)


class Storage:
    def __init__(self, activity_tracker, t):
        self.db_name = os.path.join(cfg.CURRENT_DIR, cfg.SQLDB)
        self.last_commit = t
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
        self.parseToSqlite()
        # raise Exception("No database defined")

    def parseToSqlite(self):
        # do the app parsing first so later events can read the active app
        app_parser.parse_apps(self.session, self.activity_tracker)
        app_parser.parse_windows(self.session, self.activity_tracker)
        app_parser.parse_geometries(self.session, self.activity_tracker)
        click_parser.parse_clicks(self.session)
        clip_parser.parse_clips(self.session)
        key_parser.parse_keys(self.session)
        move_parser.parse_moves(self.session)
        recorder_parser.parse_recorder(self.session)
        scroll_parser.parse_scrolls(self.session)
        # TODO add web history scraping here
        web_parser.parse_urls(self.session)

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

    def clearData(self):
        minutes_to_delete = self.activity_tracker.sniffer.delegate.prefContr.clearDataPopup.selectedItem().tag()
        text = self.activity_tracker.sniffer.delegate.prefContr.clearDataPopup.selectedItem().title()

        if minutes_to_delete == -1:
            delete_from_time = datetime.datetime.min
            delete_from_time_unix = 0
        else:
            delta = datetime.timedelta(minutes=minutes_to_delete)
            now = datetime.datetime.now()
            delete_from_time = now - delta

            now_unix = cfg.NOW()
            delete_from_time_unix = now_unix - 60*minutes_to_delete


        # delete screenshots
        screenshot_directory = os.path.expanduser(os.path.join(cfg.CURRENT_DIR,"screenshots"))
        screenshot_files = os.listdir(screenshot_directory)
        for f in screenshot_files:
            if f[0:19] > delete_from_time.strftime("%y%m%d-%H%M%S%f"):
                os.remove(os.path.join(screenshot_directory,f))

        # delete clipboard images
        clipboard_directory = os.path.expanduser(os.path.join(cfg.CURRENT_DIR,"clipboard"))
        clipboard_files = os.listdir(clipboard_directory)
        for f in clipboard_files:
            if f[0:19] > delete_from_time.strftime("%y%m%d-%H%M%S%f"):
                os.remove(os.path.join(clipboard_directory,f))

        # delete audio files
        audio_directory = os.path.expanduser(os.path.join(cfg.CURRENT_DIR,"audio"))
        audio_files = os.listdir(audio_directory)
        for f in audio_files:
            if f[0:19] > delete_from_time.strftime("%y%m%d-%H%M%S%f"):
                os.remove(os.path.join(audio_directory,f))

        # delete log files, since they only have the last 5 seconds of data,
        # we don't need to check if the data is later than the delete_from_time
        logs = os.listdir(cfg.CURRENT_DIR)
        for l in logs:
            if l[-4:] == ".log":
                os.remove(os.path.join(cfg.CURRENT_DIR,l))

        # delete data from all database tables
        # TODO may be a cleaner way to iterate through this given the table names
        self.session.query(App).filter(App.time > delete_from_time_unix).delete()
        self.session.query(AppEvent).filter(AppEvent.time > delete_from_time_unix).delete()
        self.session.query(Arrangement).filter(Arrangement.time > delete_from_time_unix).delete()
        self.session.query(Click).filter(Click.time > delete_from_time_unix).delete()
        self.session.query(Clipboard).filter(Clipboard.time > delete_from_time_unix).delete()
        self.session.query(Experience).filter(Experience.time > delete_from_time_unix).delete()
        self.session.query(Geometry).filter(Geometry.time > delete_from_time_unix).delete()
        self.session.query(Keys).filter(Keys.time > delete_from_time_unix).delete()
        self.session.query(Move).filter(Move.time > delete_from_time_unix).delete()
        self.session.query(RecordingEvent).filter(RecordingEvent.time > delete_from_time_unix).delete()
        self.session.query(Scroll).filter(Scroll.time > delete_from_time_unix).delete()
        self.session.query(Window).filter(Window.time > delete_from_time_unix).delete()
        self.session.query(WindowEvent).filter(WindowEvent.time > delete_from_time_unix).delete()

        print "Deleted last " + text + " of your history"
