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

from Cocoa import (NSEvent, NSLeftMouseUp, NSLeftMouseDown, NSLeftMouseUpMask,
                    NSLeftMouseDownMask, NSRightMouseUp, NSRightMouseDown,
                    NSRightMouseUpMask, NSRightMouseDownMask, NSScreen)

import config as cfg
import preferences
import utils_cocoa

import Quartz
from Quartz import (CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenAboveWindow,
                    kCGWindowListOptionIncludingWindow, kCGWindowListExcludeDesktopElements,
                    kCGWindowListOptionAll, kCGWindowListExcludeDesktopElements,
                    kCGNullWindowID, CGImageGetHeight, CGImageGetWidth)


class ClickRecorder:

    def __init__(self, sniffer):
        self.sniffer = sniffer

    def start_click_listener(self):
        mask = (NSLeftMouseDownMask
                | NSRightMouseDownMask) # | NSLeftMouseUpMask | NSRightMouseUpMask)

        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, self.click_handler)

    def click_handler(self, event):
        recording = preferences.getValueForPreference('recording')
        event_screenshots = preferences.getValueForPreference('eventScreenshots')
        if event_screenshots:
            self.sniffer.activity_tracker.take_screenshot()

        if recording:
            # check if the clipboard has updated
            self.sniffer.clr.get_clipboard_contents()

            # get data ready to write
            loc = NSEvent.mouseLocation()
            scr = NSScreen.screens()
            xmin = 0
            ymin = 0
            for s in scr:
                if s.frame().origin.x < xmin:
                    xmin = s.frame().origin.x
                if s.frame().origin.y < ymin:
                    ymin = s.frame().origin.y

            x = int(loc.x) - xmin
            y = int(loc.y) - ymin

            #get click type
            click_type = "Unknown"
            if event.type() == NSLeftMouseDown:
                click_type = "Left"
            elif event.type() == NSRightMouseDown:
                click_type = "Right"

            # write JSON object to clicklog file
            text = '{"time": '+ str(cfg.NOW()) + ' , "button": "' + click_type + '", "location": [' + str(x) + ',' + str(y) + ']}'
            utils_cocoa.write_to_file(text, cfg.CLICKLOG)
