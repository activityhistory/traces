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

from Cocoa import (NSEvent, NSMouseMoved, NSMouseMovedMask)

import config as cfg
import preferences
import utils_cocoa

class MoveRecorder:

    def __init__(self, sniffer):
        self.sniffer = sniffer

    def start_move_listener(self):
        mask = (NSMouseMovedMask)
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, self.move_handler)

    # TODO add tracking of duration of the move
    def move_handler(self, event):
        recording = preferences.getValueForPreference('recording')
        event_screenshots = preferences.getValueForPreference('eventScreenshots')
        if event_screenshots:
            self.sniffer.activity_tracker.take_screenshot()

        if recording:
            if event.type() == NSMouseMoved:
                loc = NSEvent.mouseLocation()
                # write JSON object to movelog file
                text = '{"time": '+ str(cfg.NOW()) + ' , "location": [' + str(int(loc.x)) + ',' + str(int(loc.y)) + ']}'
                utils_cocoa.write_to_file(text, cfg.MOVELOG)
