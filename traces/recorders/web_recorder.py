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

from models import (URL, URLEvent)
import config as cfg
import utils_cocoa
import preferences

import urlparse
import sqlite3
import os


class WebRecorder:

	def __init__(self, AppRecorder):
		# keep track of the parent AppRecorder
		self.AppRecorder = AppRecorder
		self.tabList = {}
		self.lastSafariTime = None
		self.lastFirefoxTime = None

	def getChromeURLs(self, active):
		recording = preferences.getValueForPreference('recording')
		if recording:
			Chrome = SBApplication.applicationWithBundleIdentifier_("com.google.Chrome")
			windows = Chrome.windows()
			windowList = {}
			tabList = {}

			# set first tab and first window to active if browser is active
			firstWindow = active
			firstTab = active

			for window in windows:
				#TODO need to find way to tell if app is onscreen
				cwid = window.id()
				name = 'Chrome ' + str(cwid)
				bounds = {'x':window.bounds().origin.x, 'y':window.bounds().origin.y, 'width':window.bounds().size.width, 'height':window.bounds().size.height}
			  	tabs = window.tabs()
				if firstWindow:
					firstWindow = False
			  	for tab in tabs:
					tabList[tab.id()] = {'active': firstTab, 'title': str(tab.title()), 'url': str(tab.URL()), 'host': urlparse.urlparse(str(tab.URL())).hostname}
					if firstTab:
						firstTab = False
				windowList[cwid] = {'active':firstWindow, 'name': name, 'bounds': bounds, 'tabs': tabList}
				tabList = {}

			return windowList

	def getSafariURLs(self, active):
		#TODO determine way to get window and tab info from safari

		# return list of safari windows and urls
		return {}

### Should not need these browser callbacks once the above functions are implemented
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

			#TODO check if we get all tabs from multiple windows.
			# Is tab.id uniqe across all windows, or duplicated (i.e. window 1
			# has tabs 1, 2, 3 and window 2 has tabs 1, 2, 3, 4)
			for window in windows:
			  tabs = window.tabs()
			  for tab in tabs:
					self.tabList[tab.id()] = {'title': str(tab.title()), 'id': str(tab.id()), 'url': str(tab.URL()), 'host': urlparse.urlparse(str(tab.URL())).hostname}

			closedTabs = set(oldTabList.keys()) - set(self.tabList.keys())
			openedTabs = set(self.tabList.keys()) - set(oldTabList.keys())

			# take screenshot
			eventScreenshots = preferences.getValueForPreference('eventScreenshots')
			if eventScreenshots:
				self.AppRecorder.sniffer.activity_tracker.take_screenshot()

			# get list of urls from the database
			db_urls = session.query(URL).all()
			urls = [u.url for u in db_urls]

			# check if any recently opened tabs are not yet in the database
			for t in openedTabs:
				if tabList[t]['url'] not in urls:
					url_to_add = URL(t, app_name)
					session.add(url_to_add)

					#TODO need to find way to commit!
					activity_tracker.storage.sqlcommit()

					# update our local url list
					db_urls = session.query(URL).all()
					urls = [u.url for u in db_urls]

				# may need this later to write url event
				# uid = urls.index(tabList[t]['url']) + 1 # array starts at 0, database ids a 1

			# # write to browser log file about event
			# for tab in closedTabs:
			# 	text = '{"time": ' + str(t) + ', "browser": "Google Chrome", "url": "' + str(oldTabList[tab]['url']) + '", "title": "' + str(oldTabList[tab]['title']) + '", "event": "Close"' +' }'
			# 	utils_cocoa.write_to_file(text, cfg.URLLOG)
			#
			# for tabId, tabInfo in self.tabList.iteritems():
			# 	event = 'None'
			# 	if tabId in openedTabs:
			# 		text = '{"time": ' + str(t) + ', "browser": "Google Chrome", "url": "' + tabInfo['url'] + '", "title": "' + tabInfo['title'] + '", "event": ' + '"Open"' +' }'
			# 		utils_cocoa.write_to_file(text, cfg.URLLOG)
			# 	elif tabInfo['url'] != oldTabList[tabId]['url']:
			# 		text = '{"time": ' + str(t) + ', "browser": "Google Chrome", "url": "' + tabInfo['url'] + '", "title": "' + tabInfo['title'] + '", "event": ' + '"Open"' +' }'
			# 		utils_cocoa.write_to_file(text, cfg.URLLOG)
			# 		text = '{"time": ' + str(t) + ', "browser": "Google Chrome", "url": "' + oldTabList[tabId]['url'] + '", "title": "' + oldTabList[tabId]['title'] + '", "event": ' + '"Close"' +' }'
			# 		utils_cocoa.write_to_file(text, cfg.URLLOG)

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

			# looks like safari writes every ~10 seconds so offset by 10. Add an extra 0.1 sec for roundoff issues
			safariTimeOffset = int(utils_cocoa.unix_to_safari(cfg.NOW())) - 9.9
			if self.lastSafariTime < safariTimeOffset:
				self.lastSafariTime = safariTimeOffset

			for entry in c.fetchall():
				url = entry[2]
				title = entry[1]
				time = entry[0]
				if self.lastSafariTime < time:
					self.lastSafariTime = time
				text = '{"time": ' + str(utils_cocoa.safari_to_unix(time)) + ', "browser": "Safari", "url": "' + str(url) + '", "title": "' + str(title) + '", "event": ' + '"Open"' +' }'
				utils_cocoa.write_to_file(text, cfg.URLLOG)

		if not recording:
			self.lastSafariTime = None

	def firefoxCallback(self, **kwargs):
		recording = preferences.getValueForPreference('recording')
		if recording:
			print 'FIREFOX CALLBACK'

			notification_title = str(kwargs['notification'])[2:]

			if notification_title != "MenuItemSelected" and notification_title != "TitleChanged":
				self.AppRecorder.windowCallback(**kwargs)

			if self.lastFirefoxTime == None:
				self.lastFirefoxTime = int(utils_cocoa.unix_to_firefox(cfg.NOW()))
				return

			profiles = []
			profFile = open(os.path.expanduser('~/Library/Application Support/Firefox/profiles.ini'))
			for line in profFile:
				if line[:5] == 'Path=':
					profiles.append(line[5:-1])
			for profile in profiles:
				conn = sqlite3.connect(os.path.expanduser('~/Library/Application Support/Firefox/' + profile + '/places.sqlite'))
				c = conn.cursor()
				c.execute("SELECT visit_date, title, url FROM moz_historyvisits LEFT JOIN moz_places ON moz_historyvisits.place_id == moz_places.id where visit_date > " + str(self.lastFirefoxTime))

				# offset by 10. Add an extra 0.1 sec for roundoff issues
				ffTimeOffset = int(utils_cocoa.unix_to_firefox(cfg.NOW())) - 9.9
				if self.lastFirefoxTime < ffTimeOffset:
					self.lastFirefoxTime = ffTimeOffset

				for entry in c.fetchall():
					print '143'
					print entry
					url = entry[2]
					title = entry[1]
					time = entry[0]
					if self.lastFirefoxTime < time:
						self.lastFirefoxTime = time
					text = '{"time": ' + str(utils_cocoa.firefox_to_unix(time)) + ', "browser": "Firefox", "url": "' + str(url) + '", "title": "' + str(title) + '", "event": ' + '"Open"' +' }'
					utils_cocoa.write_to_file(text, cfg.URLLOG)

		if not recording:
			self.lastFirefoxTime = None

	def closeChrome(self):
		for tabId, tabInfo in self.tabList.iteritems():
			event = 'Close'
			text = '{"time": ' + str(t) + ', "browser": "Google Chrome", "url": "' + tabInfo['url'] + '", "title": "' + tabInfo['title'] + '", "event": ' + '"Close"' +' }'
			utils_cocoa.write_to_file(text, cfg.URLLOG)

		self.tabList = {}
