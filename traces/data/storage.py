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

import config as cfg

import mongo.key_parser
import mongo.click_parser
import mongo.scroll_parser
import mongo.move_parser
import mongo.app_parser


class Storage:
    def __init__(self):
      #TODO need to ensure that MongoDB is running so we can use it without
      # throwing an error


    def parseLogs(self):
      if (cfg.STORAGE is "mongo"):
          self.parseToMongo()
      elif: 
          self.parseToSQLite()
      else:
          raise Exception("No database defined")

    def parseToMongo(self):
      # open database server
      client = pymongo.MongoClient()
      db = client[cfg.DB]
      try:
          # parse all the relevant log files
          key_parser.parse_keys(db)
          click_parser.parse_clicks(db)
          scroll_parser.parse_scrolls(db)
          move_parser.parse_moves(db)
          app_parser.parse_apps(db)
          app_parser.parse_windows(db)
          app_parser.parse_geometries(db)
      except:
          print "Had an issue with parsing"
        
    def parseToSQLite(self):
      pass
    
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
