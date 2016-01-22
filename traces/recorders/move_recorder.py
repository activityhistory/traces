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

from Cocoa import (NSEvent, NSMouseMoved, NSMouseMovedMask, NSScreen)

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

				# get all the image size information
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

				# write JSON object to movelog file
				text = '{"time": '+ str(cfg.NOW()) + ' , "location": [' + str(x) + ',' + str(y) + ']}'
				utils_cocoa.write_to_file(text, cfg.MOVELOG)
