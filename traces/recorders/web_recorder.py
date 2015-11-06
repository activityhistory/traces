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
import objc

from AppKit import *
from Foundation import *
from ScriptingBridge import *
from Quartz import (CFRunLoopRun, kCGWindowListOptionAll,
					CGWindowListCopyWindowInfo, kCGNullWindowID,
					kCGWindowListExcludeDesktopElements)

import accessibility as acc # https://github.com/atheriel/accessibility

import config as cfg
import utils_cocoa
import preferences


class WebRecorder:

	def __init__(self, AppRecorder):
		# keep track of the parent AppRecorder
		self.AppRecorder = AppRecorder
		self.tabList = {}
	
	def chromeCallback(self, **kwargs):
		recording = preferences.getValueForPreference('recording')
		if recording:
			# get event info
			t = cfg.NOW()
			notification_title = str(kwargs['notification'])[2:] # remove 'AX' from front of event names before we save that info

			if notification_title != "MenuItemSelected" and notification_title != "TitleChanged":
				self.AppRecorder.windowCallback(**kwargs)
				return
			
			Chrome = SBApplication.applicationWithBundleIdentifier_("com.google.Chrome")
			windows = Chrome.windows()
			oldTabList = self.tabList
			self.tabList = {}

			for window in windows:
			  tabs = window.tabs()
			  for tab in tabs:
					self.tabList[tab.id()] = {'title': str(tab.title()), 'id': str(tab.id()), 'url': str(tab.URL())}
			
			closedTabs = set(oldTabList.keys()) - set(self.tabList.keys())
			openedTabs = set(self.tabList.keys()) - set(oldTabList.keys())

			# take screenshot
			eventScreenshots = preferences.getValueForPreference('eventScreenshots')
			if eventScreenshots:
				ar.sniffer.activity_tracker.take_screenshot()
			
			# write to browser log file about event
			for tab in closedTabs:
				text = '{"time": ' + str(t) + ' , "tabId": "' + str(tab) + '", "event": "Closed"' +' }'
				utils_cocoa.write_to_file(text, cfg.TABLOG)

			for tabId, tabInfo in self.tabList.iteritems():
				event = 'None'
				if tabId in openedTabs:
					event = 'Opened'
				elif self.tabList[tabId]['url'] != oldTabList[tabId]['url']:
					event = 'Modified'
				text = '{"time": ' + str(t) + ' , "tabId": "' + str(tabId) + '", "title": "' + tabInfo['title'] + '", "url": ' + tabInfo['url'] + '", "event": ' + event +' }'
				utils_cocoa.write_to_file(text, cfg.TABLOG)
			
	def getTabs(self, windowList):
		windowList['tabs'] = {}
		Chrome = SBApplication.applicationWithBundleIdentifier_("com.google.Chrome")
		windows = Chrome.windows()
		
		for window in windows:
		  tabs = window.tabs()
		  windowList['tabs'][window.id()] = []
		  for tab in tabs:
				windowList['tabs'][window.id()].append(str(tab.title()))

	def closeChrome(self):
		for tabId, tabInfo in self.tabList.iteritems():
			event = 'Closed'
			text = '{"time": ' + str(t) + ' , "tabId": "' + str(tabId) + '", "title": "' + tabInfo['title'] + '", "url": ' + tabInfo['url'] + '", "event": ' + event +' }'
			utils_cocoa.write_to_file(text, cfg.TABLOG)
		
		self.tabList = {}
