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

from Cocoa import (NSEvent, NSScrollWheel, NSScrollWheelMask)

import config as cfg
import preferences
import utils_cocoa

class ScrollRecorder:

	def __init__(self, sniffer):
		self.sniffer = sniffer

	def start_scroll_listener(self):
		mask = (NSScrollWheelMask)
		NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, self.scroll_handler)

	# TODO add tracking of duration of scroll
	def scroll_handler(self, event):
		recording = preferences.getValueForPreference('recording')
		event_screenshots = preferences.getValueForPreference('eventScreenshots')
		if event_screenshots:
			self.sniffer.activity_tracker.take_screenshot()

		if recording:
			if event.type() == NSScrollWheel:
			# write JSON object to scrolllog file
				text = '{"time": '+ str(cfg.NOW()) + ' , "distance": [' + str(event.deltaX()) + ',' + str(event.deltaY()) + '], "window_number": ' + str(event.windowNumber()) + '}'
				utils_cocoa.write_to_file(text, cfg.SCROLLLOG)
