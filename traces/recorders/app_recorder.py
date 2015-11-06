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
from Quartz import (CFRunLoopRun, kCGWindowListOptionAll,
					CGWindowListCopyWindowInfo, kCGNullWindowID,
					kCGWindowListExcludeDesktopElements)

import accessibility as acc # https://github.com/atheriel/accessibility

from web_recorder import WebRecorder
import config as cfg
import utils_cocoa
import preferences


class AppRecorder:

	def __init__(self, sniffer):
		# keep track of the sniffer that launched this app recorder
		self.sniffer = sniffer

		# keep track of app listeners so they don't get garbage collected
		self.watched = {}

		# keep track of screen geometry
		self.apps_and_windows = {}

		# subclass definitions
		self.wr = WebRecorder(self)

### Application event callbacks ###
	def appLaunchCallback_(self, notification):
		recording = preferences.getValueForPreference('recording')
		# get event info
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		name = utils_cocoa.ascii_encode(app.localizedName())
		pid = int(app.processIdentifier())

		# create app listener for this app's window events
		if app.activationPolicy() == 0:
			mess = acc.create_application_ref(pid = pid)
			mess.set_callback(self.windowCallback)
			mess.watch("AXMoved", "AXWindowResized", "AXFocusedWindowChanged",
						"AXWindowCreated","AXWindowMiniaturized",
						"AXWindowDeminiaturized")
			self.watched[pid] = mess

			if recording:
				# log that the application launched
				text = '{"time": '+ str(t) + ' , "type": "Launch", "app": "' + name + '"}'
				utils_cocoa.write_to_file(text, cfg.APPLOG)

			# take a screenshot
			eventScreenshots = preferences.getValueForPreference('eventScreenshots')
			if eventScreenshots:
				self.sniffer.activity_tracker.take_screenshot()

		# check if the screen geometry changed and update active window
		self.updateWindowList()

	def appTerminateCallback_(self, notification):
		recording = preferences.getValueForPreference('recording')

		# get event info
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		#TODO find out why we are getting no name from the app terminate
		name = utils_cocoa.ascii_encode(app.localizedName())
		pid = int(app.processIdentifier())

		# let app listener be garbage collected by removing our saved reference to it
		if pid in self.watched.keys():
			del self.watched[pid]
			# watcher = self.watched[p]

			if recording:
				# log the the application has closed
				text = '{"time": '+ str(t) + ' , "type": "Terminate", "app": "' + name + '"}'
				utils_cocoa.write_to_file(text, cfg.APPLOG)

			if utils_cocoa.ascii_encode(app.localizedName()) == "Google Chrome":
				wr.closeChrome()

		# check if the screen geometry changed and update active window
		self.updateWindowList()

	def appActivateCallback_(self, notification):
		recording = preferences.getValueForPreference('recording')

		# get event info
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		name = utils_cocoa.ascii_encode(app.localizedName())
		pid = int(app.processIdentifier())

		# log that the application has become active
		if pid in self.watched.keys() and recording:
			text = '{"time": '+ str(t) + ' , "type": "Activate", "app": "' + name + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		# take screenshot
		eventScreenshots = preferences.getValueForPreference('eventScreenshots')
		if eventScreenshots:
			self.sniffer.activity_tracker.take_screenshot()

		# check if the screen geometry changed and update active window
		self.updateWindowList()

	def appDeactivateCallback_(self, notification):
		recording = preferences.getValueForPreference('recording')

		# get event info
		t = cfg.NOW()

		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		# only save the info if we have app information
		# we don't get app information when this is thrown after an app closes
		if app.processIdentifier() == -1:
			return
		name = utils_cocoa.ascii_encode(app.localizedName())
		pid = int(app.processIdentifier())

		# log that the application has become inactive
		if pid in self.watched.keys() and recording:
			text = '{"time": '+ str(t) + ' , "type": "Deactivate", "app": "' + name + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		# check if the screen geometry changed and update active window
		self.updateWindowList()

### Window event callbacks ###
	#TODO make function more robust so it does not fail if some of the accessibility data is not available
	def windowCallback(self, **kwargs):
		recording = preferences.getValueForPreference('recording')
		if recording:
			# get event info
			t = cfg.NOW()
			notification_title = str(kwargs['notification'])[2:-1] # remove 'AX' from front of event names before we save that info
			# TODO this app title may not match what we get from app.localizedName()
			# find way to reconcile
			app_title = utils_cocoa.ascii_encode(kwargs['element']['AXTitle'])

			# take screenshot
			eventScreenshots = preferences.getValueForPreference('eventScreenshots')
			if eventScreenshots:
				self.sniffer.activity_tracker.take_screenshot()

			# when miniaturized, we may not be able to get window title and position data
			if notification_title == "WindowMiniaturized":
				# write to window log file about event
				text = '{"time": '+ str(t) + ' , "type": "' + notification_title + '", "app": "' + app_title + '" }'
				utils_cocoa.write_to_file(text, cfg.WINDOWLOG)

			# all other events should let us get title and postiion data
			else:
				# get the relevant window data
				title = utils_cocoa.ascii_encode(kwargs['element']['AXFocusedWindow']['AXTitle'])
				position = str(kwargs['element']['AXFocusedWindow']['AXPosition'])
				size = str(kwargs['element']['AXFocusedWindow']['AXSize'])

				# write to window log file about event
				text = '{"time": ' + str(t) + ' , "type": "' + notification_title + '", "app": "' + app_title + '", "window": "' + title + '", "position": ' + position + ' , "size": ' + size +' }'
				utils_cocoa.write_to_file(text, cfg.WINDOWLOG)

			# get most recent screen geometry and update active window
			self.updateWindowList()

	def updateWindowList(self):
		# get an early timestamp
		recording = preferences.getValueForPreference('recording')
		t = cfg.NOW()

		if recording:
			# clear our past geometry and active window
			self.apps_and_windows = {}
			active_window = None

			# get list of applications that show up in the dock
			workspace = NSWorkspace.sharedWorkspace()
			activeApps = workspace.runningApplications()
			regularApps = []
			for app in activeApps:
				if app.activationPolicy() == 0:
					regularApps.append(app)

			# save app info to dictionary
			for app in regularApps:
				name = utils_cocoa.ascii_encode(app.localizedName())
				active = app.isActive()
				pid = app.processIdentifier()
				d = {'name': name, 'active': active, 'windows':{}}
				if name == "Google Chrome":
					d['browser'] = True
				self.apps_and_windows[int(pid)] = d # store app data by pid

				# get title of the active window if possible
				if active:
					try:
						mess = self.watched[pid]
						active_window = mess['AXFocusedWindow']['AXTitle']
					except:
						pass

			# add list of current windows
			options = kCGWindowListOptionAll + kCGWindowListExcludeDesktopElements
			windows = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
			for window in windows:
				try:
					# get window data
					owning_app_pid = window['kCGWindowOwnerPID']
					window_layer = window['kCGWindowLayer']
					name = utils_cocoa.ascii_encode(window['kCGWindowName'])
					window_id = window['kCGWindowNumber']
					bounds = window['kCGWindowBounds']
					win_bounds = {'width':bounds['Width'], 'height':bounds['Height'], 'x':bounds['X'], 'y':bounds['Y']}
					active = False
					if window['kCGWindowName'] == active_window:
						active = True

					# unless it has a name and is on the top layer, we don't count it
					if owning_app_pid in self.apps_and_windows and window_layer == 0 and name:
						# add window data to the app_window dictionary
						window_dict = {'name': name, 'bounds': win_bounds, 'active': active}
						self.apps_and_windows[owning_app_pid]['windows'][window_id] = window_dict
						if d['browser']:
							self.apps_and_windows[owning_app_pid] = wr.getTabs(self.apps_and_windows[owning_app_pid])
				except:
					pass

			# write self.apps_and_windows to a geometry file
			text = '{"time": ' + str(t) + ', "geometry": ' +  str(self.apps_and_windows) + "}"
			utils_cocoa.write_to_file(text, cfg.GEOLOG)

### Computer sleep/wake callbacks ###
	def sleepCallback_(self, notification):
		recording = preferences.getValueForPreference('recording')
		if recording:
			t = cfg.NOW()
			text = '{"time": '+ str(t) + ' , "type": "Sleep"}'
			utils_cocoa.write_to_file(text, cfg.RECORDERLOG)

	def wakeCallback_(self, notification):
		recording = preferences.getValueForPreference('recording')
		if recording:
			t = cfg.NOW()
			text = '{"time": '+ str(t) + ' , "type": "Wake"}'
			utils_cocoa.write_to_file(text, cfg.RECORDERLOG)

		# take a screenshot
		eventScreenshots = preferences.getValueForPreference('eventScreenshots')
		if eventScreenshots:
			self.sniffer.activity_tracker.take_screenshot()

		# get updated list of applications and windows
		self.updateWindowList()

### Manager the event listeners ###
	def start_app_observers(self):
		recording = preferences.getValueForPreference('recording')
        # prompt user to grant accessibility access to Traces, if not already granted
		acc.is_enabled()

		# get an early timestamp
		t = cfg.NOW()

		# create listeners for application events
		workspace = NSWorkspace.sharedWorkspace()
		nc = workspace.notificationCenter()
		s = objc.selector(self.appLaunchCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidLaunchApplicationNotification', None)
		s = objc.selector(self.appTerminateCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidTerminateApplicationNotification', None)
		s = objc.selector(self.appActivateCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidActivateApplicationNotification', None)
		s = objc.selector(self.appDeactivateCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidDeactivateApplicationNotification', None)

        # create listeners for system events
		s = objc.selector(self.wakeCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidWakeNotification', None)
		s = objc.selector(self.sleepCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceWillSleepNotification', None)

		# other events that may be useful to track in the future
        # https://developer.apple.com/library/mac/documentation/Cocoa/Reference/ApplicationKit/Classes/NSWorkspace_Class/
		# NSWorkspaceDidHideApplicationNotification
		# NSWorkspaceDidUnhideApplicationNotification
		# NSWorkspaceActiveSpaceDidChangeNotification
        # NSWorkspaceWillPowerOffNotification
        # NSWorkspaceDidPerformFileOperationNotification

        # get list of active applications
		activeApps = workspace.runningApplications()
		regularApps = []
		for app in activeApps:
			if app.activationPolicy() == 0: # those that show up in the Dock
				regularApps.append(app)

        # listen for window events of these applications
		for app in regularApps:
			try:
				p = int(app.processIdentifier())
				name = utils_cocoa.ascii_encode(app.localizedName())
				if name != "Google Chrome":
					mess = acc.create_application_ref(pid=p)
					mess.set_callback(self.windowCallback)
					mess.watch("AXMoved", "AXWindowResized", "AXFocusedWindowChanged",
							"AXWindowCreated","AXWindowMiniaturized",
							"AXWindowDeminiaturized") # AXMainWindowChanged
					self.watched[p] = mess # we need to maintain the listener or it will be deleted on cleanup
				else:
					mess = acc.create_application_ref(pid=p)
					mess.set_callback(self.wr.chromeCallback)
					mess.watch("AXMoved", "AXWindowResized", "AXFocusedWindowChanged",
							"AXWindowCreated","AXWindowMiniaturized",
							"AXWindowDeminiaturized","AXMenuItemSelected", "AXTitleChanged") # AXMainWindowChanged
					self.watched[p] = mess # we need to maintain the listener or it will be deleted on cleanup

				if recording:
					# log that the app is open
					text = '{"time": '+ str(t) + ' , "type": "Launch: Recording Started", "app": "' + name + '"}'
					utils_cocoa.write_to_file(text, cfg.APPLOG)

			except:
				raise
				print "Could not create event listener for application: " + str(name)

		# get inital list of windows and add window listeners
		self.updateWindowList()

		# start event loop to track events from other applications
		CFRunLoopRun()

	def stop_app_observers(self):
		recording = preferences.getValueForPreference('recording')
		t = cfg.NOW()

        # get workspace and list of all applications
		workspace = NSWorkspace.sharedWorkspace()
		activeApps = workspace.runningApplications()

		# let app observers be garabage collected
		self.watched = {}

		if recording:
	        # prune list of applications to apps that appear in the dock
			regularApps = []
			for app in activeApps:
				if app.activationPolicy() == 0:
					regularApps.append(app)

	        # listen for window events of these applications
			for app in regularApps:
				name = utils_cocoa.ascii_encode(app.localizedName())
				# log that the app recording will stop
				text = '{"time": '+ str(t) + ' , "type": "Terminate: Recording Stopped", "app": "' + name + '"}'
				utils_cocoa.write_to_file(text, cfg.APPLOG)
