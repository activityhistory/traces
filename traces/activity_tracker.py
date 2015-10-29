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
import datetime
import threading

from Foundation import *
from AppKit import *
from Cocoa import NSNotificationCenter

from data.storage import Storage

import preferences
import config as cfg
import sniff_cocoa as sniffer


class ActivityTracker:
    def __init__(self):

        # variables for managing loops
        self.last_screenshot = cfg.NOW()
        self.screenshotTimer = None

        self.last_parse = cfg.NOW()
        self.parseTimer = None

    def checkLoops(self):
        # if we're recording, start the screenshot and parsing loops
        recording = preferences.getValueForPreference('recording')
        if(recording):
            self.startLoops()
        else:
            self.stopLoops()

    def startLoops(self):
        # Timers for taking screenshots when idle, and parsing log files
        self.screenshotTimer = threading.Timer(1.0, self.run_screenshot_loop)
        self.screenshotTimer.start()
        self.parseTimer = threading.Timer(cfg.PARSEDELAY, self.parseLogs)
        self.parseTimer.start()

    def stopLoops(self):
        try:
            if self.screenshotTimer:
                self.screenshotTimer.cancel()
            if self.parseTimer:
                self.parseTimer.cancel()
        except:
            print "Had trouble stopping screenshot and parsing loops"

    def run_screenshot_loop(self):
        # take a screenshot if computer is idle and appropriate amount of time has passed
        screenshot_time_max = preferences.getValueForPreference('imageTimeMax')
        periodic = preferences.getValueForPreference('periodicScreenshots')
        time_since_last_screenshot = cfg.NOW() - self.last_screenshot
        if (time_since_last_screenshot > screenshot_time_max):
            if periodic:
                self.take_screenshot()
            time_since_last_screenshot = 0.0
        sleep_time = screenshot_time_max - time_since_last_screenshot + 0.001 # add a milisecond for good measure
        self.screenshotTimer = threading.Timer(sleep_time,self.run_screenshot_loop)
        self.screenshotTimer.start()

    def take_screenshot(self):
      # check screenshot preferences
      recording = preferences.getValueForPreference('recording')
      screenshots_active = preferences.getValueForPreference('screenshots')
      screenshot_time_min = preferences.getValueForPreference('imageTimeMin') / 1000.0

      # take a screenshot if preferences allow
      if (screenshots_active and recording
        and (cfg.NOW() - self.last_screenshot) > screenshot_time_min) :
          try:
              # get filename
              filename = datetime.datetime.now().strftime("%y%m%d-%H%M%S%f")
              y = filename[0:2]
              m = filename[2:4]
              d = filename[4:6]
              h = filename[7:9]
              folder = os.path.join(cfg.CURRENT_DIR,"screenshots",y,m,d,h)
              if not os.path.exists(folder):
                  os.makedirs(folder)
              path = os.path.join(folder,""+filename+".jpg")

              # take screenshot
              self.sniffer.screenshot(path)
              self.last_screenshot = cfg.NOW()
          except:
              print "There was an error with saving a screenshot"

    def restartScreenshotLoop(self):
        if self.screenshotTimer:
            self.screenshotTimer.cancel()
        self.run_screenshot_loop()

    def parseLogs(self):
        self.storage.parseLogs()

        self.last_parse = cfg.NOW()
        self.parseTimer = threading.Timer(cfg.PARSEDELAY, self.parseLogs)
        self.parseTimer.start()

    # not sure if we need this helper function in this file
    # def clearData(self):
    #     self.storage.clearData()
    #     print "You asked to delete history"

    def run(self):
        # hook up the sniffer
        self.sniffer = sniffer.Sniffer(self)

        # create object to manage database storage
        self.storage = Storage(self, cfg.NOW())

        self.sniffer.run()
