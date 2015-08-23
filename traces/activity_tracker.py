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

        # variables for tracking loops
        self.last_screenshot = cfg.NOW()
        self.screenshotTimer = None

        self.last_parse = cfg.NOW()
        self.parseTimer = None
        
        self.storage = Storage()

    def checkLoops(self):
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
            print "Had trouble stopping loops"

    def run_screenshot_loop(self):
        screenshot_time_max = preferences.getValueForPreference('imageTimeMax')
        time_since_last_screenshot = cfg.NOW() - self.last_screenshot
        if (time_since_last_screenshot > screenshot_time_max):
            self.take_screenshot()
            time_since_last_screenshot = 0.0
        sleep_time = screenshot_time_max - time_since_last_screenshot + 0.01
        self.screenshotTimer = threading.Timer(sleep_time,self.run_screenshot_loop)
        self.screenshotTimer.start()

    def take_screenshot(self):
      # check screenshot preferences
      screenshots_active = preferences.getValueForPreference('screenshots')
      screenshot_time_min = preferences.getValueForPreference('imageTimeMin') / 1000.0

      if (screenshots_active
        and (cfg.NOW() - self.last_screenshot) > screenshot_time_min) :
          try:
              # get filename
              folder = os.path.join(cfg.CURRENT_DIR,"screenshots")
              filename = datetime.datetime.now().strftime("%y%m%d-%H%M%S%f")
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

    def clearData(self):
        self.storage.clearData()
        print "You asked to delete history"

    # TODO make it easier for others to add parser files for extensions
    def parseLogs(self):
        print "Parsing log files."

        self.storage.parseLogs()

        self.last_parse = cfg.NOW()
        self.parseTimer = threading.Timer(cfg.PARSEDELAY, self.parseLogs)
        self.parseTimer.start()

    def run(self):
        # TODO add platform detection before calling appropriate sniffer
        # hook up the sniffer
        self.sniffer = sniffer.Sniffer(self)
        self.sniffer.run()
