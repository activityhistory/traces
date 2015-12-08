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

from Foundation import *
from ScriptingBridge import *

import config as cfg
import utils_cocoa
import preferences
import sqlite3
import os


class WebRecorder:

	def __init__(self, AppRecorder):
		# keep track of the parent AppRecorder
		self.AppRecorder = AppRecorder
		self.tabList = {}
		self.lastSafariTime = None
	
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
				self.AppRecorder.sniffer.activity_tracker.take_screenshot()

			# write to browser log file about event
			for tab in closedTabs:
				text = '{"time": ' + str(t) + ', "browser": "Google Chrome", "url": "' + str(oldTabList[tab]['url']) + '", "title": "' + str(oldTabList[tab]['title']) + '", "event": "Closed"' +' }'
				utils_cocoa.write_to_file(text, cfg.URLLOG)

			for tabId, tabInfo in self.tabList.iteritems():
				event = 'None'
				if tabId in openedTabs:
					text = '{"time": ' + str(t) + ', "browser": "Google Chrome", "url": "' + tabInfo['url'] + '", "title": "' + tabInfo['title'] + '", "event": ' + '"Opened"' +' }'
					utils_cocoa.write_to_file(text, cfg.URLLOG)
				elif tabInfo['url'] != oldTabList[tabId]['url']:
					text = '{"time": ' + str(t) + ', "browser": "Google Chrome", "url": "' + tabInfo['url'] + '", "title": "' + tabInfo['title'] + '", "event": ' + '"Opened"' +' }'
					utils_cocoa.write_to_file(text, cfg.URLLOG)
					text = '{"time": ' + str(t) + ', "browser": "Google Chrome", "url": "' + oldTabList[tabId]['url'] + '", "title": "' + oldTabList[tabId]['title'] + '", "event": ' + '"Closed"' +' }'
					utils_cocoa.write_to_file(text, cfg.URLLOG)

	def safariCallback(self, **kwargs):
		recording = preferences.getValueForPreference('recording')
		if recording:

			notification_title = str(kwargs['notification'])[2:]

			if notification_title != "MenuItemSelected" and notification_title != "TitleChanged":
				self.AppRecorder.windowCallback(**kwargs)

			if self.lastSafariTime == None:
				self.lastSafariTime = int(utils_cocoa.unix_to_safari(cfg.NOW()))
				return

			conn = sqlite3.connect(os.path.expanduser('~/Library/Safari/History.db'))
			c = conn.cursor()
			c.execute("SELECT visit_time, title, url FROM history_visits LEFT JOIN history_items ON history_visits.history_item == history_items.id where visit_time > " + str(self.lastSafariTime))

			# looks like safari writes every ~10 seconds so offset by 10. Add an extra 9.9 for roundoff issues
			safariTimeOffset = int(utils_cocoa.unix_to_safari(cfg.NOW())) - 9.9
			if self.lastSafariTime < safariTimeOffset:
				self.lastSafariTime = safariTimeOffset

			for entry in c.fetchall():
				url = entry[2]
				title = entry[1]
				time = entry[0]
				if self.lastSafariTime < time:
					self.lastSafariTime = time
				text = '{"time": ' + str(utils_cocoa.safari_to_unix(time)) + ', "browser": "Safari", "url": "' + str(url) + '", "title": "' + str(title) + '", "event": ' + '"Opened"' +' }'
				utils_cocoa.write_to_file(text, cfg.URLLOG)

		if not recording:
			self.lastSafariTime = None

	def firefoxCallback(self, **kwargs):
		print 'ff'

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
			utils_cocoa.write_to_file(text, cfg.URLLOG)
		
		self.tabList = {}
