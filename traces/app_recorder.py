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

import config as cfg
import utils_cocoa


class AppRecorder:

	def __init__(self, sniffer):
		# keep track of the sniffer that launched this app recorder
		self.sniffer = sniffer

		# keep track of app listeners so they don't get garbage collected
		self.watched = {}

		# keep track of screen geometry
		self.apps_and_windows = {}


	### Application event callbacks ###
	def appLaunchCallback_(self, notification):
		# get event info
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		name = utils_cocoa.ascii_encode(app.localizedName())
		p = int(app.processIdentifier())

		# create app listener for this app's window events
		if app.activationPolicy() == 0:
			mess = acc.create_application_ref(pid = p)
			mess.set_callback(self.windowCallback)
			mess.watch("AXMoved", "AXWindowResized", "AXFocusedWindowChanged",
						"AXWindowCreated","AXWindowMiniaturized",
						"AXWindowDeminiaturized")
			self.watched[p] = mess

			# log that the application launched
			text = '{"time": '+ str(t) + ' , "type": "Launch", "app": "' + name + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		# check if the screen geometry changed and update active window
		self.updateWindowList()

	def appTerminateCallback_(self, notification):
		# get event info
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		name = utils_cocoa.ascii_encode(app.localizedName())
		p = int(app.processIdentifier())

		# let app listener be garbage collected by removing our saved reference to it
		if p in self.watched.keys():
			del self.watched[p]
			# watcher = self.watched[p]

			# log the the application has closed
			text = '{"time": '+ str(t) + ' , "type": "Terminate", "app": "' + name + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		# check if the screen geometry changed and update active window
		self.updateWindowList()

	def appActivateCallback_(self, notification):
		# get event info
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		name = utils_cocoa.ascii_encode(app.localizedName())
		p = int(app.processIdentifier())

		# log that the application has become active
		if p in self.watched.keys():
			text = '{"time": '+ str(t) + ' , "type": "Activate", "app": "' + name + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		# check if the screen geometry changed and update active window
		self.updateWindowList()

	def appDeactivateCallback_(self, notification):
		# get event info
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		name = utils_cocoa.ascii_encode(app.localizedName())
		p = int(app.processIdentifier())

		# log that the application has become inactive
		if p in self.watched.keys():
			text = '{"time": '+ str(t) + ' , "type": "Deactivate", "app": "' + name + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		# check if the screen geometry changed and update active window
		self.updateWindowList()

	#TODO we may not need to track app hide and unhide events
	# these are not miniturization events, those are tracked at the window level
	def appHideCallback_(self, notification):
		# get event info
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		name = utils_cocoa.ascii_encode(app.localizedName())
		p = int(app.processIdentifier())

		# log that the application had been hidden
		if p in self.watched.keys():
			text = '{"time": '+ str(t) + ' , "type": "Hide", "app": "' + name + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		# check if the screen geometry changed and update active window
		self.updateWindowList()

	def appUnhideCallback_(self, notification):
		# get event info
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		name = utils_cocoa.ascii_encode(app.localizedName())
		p = int(app.processIdentifier())

		# log that the application had been unhidden
		if p in self.watched.keys():
			text = '{"time": '+ str(t) + ' , "type": "Unhide", "app": "' + name + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		# check if the screen geometry changed and update active window
		self.updateWindowList()


	### Window event callbacks ###
	def windowCallback(self, **kwargs):
		# get event info
		t = cfg.NOW()
		notification_type = kwargs['notification']
		# remove 'AX' from front of event names before we save that info
		notification_title = str(kwargs['notification'])[2:-1]
		app_title = kwargs['element']['AXTitle']

		# when miniaturized, we may not be able to get window title and position data
		if notification_type == "AXWindowMiniaturized":
			# write to window log file about event
			text = '{"time": '+ str(t) + ' , "type": "' + notification_title + '", "app": "' + app_title + '" }'
			utils_cocoa.write_to_file(text, cfg.WINDOWLOG)

		# all other events should let us get title and postiion data
		else:
			# get the relevant window data
			title = kwargs['element']['AXFocusedWindow']['AXTitle']
			position = str(kwargs['element']['AXFocusedWindow']['AXPosition'])
			size = str(kwargs['element']['AXFocusedWindow']['AXSize'])

			# write to window log file about event
			text = '{"time": ' + str(t) + ' , "type": "' + notification_title + '", "app": "' + app_title + '", "window": "' + title + '", "position": ' + position + ' , "size": ' + size +' }'
			utils_cocoa.write_to_file(text, cfg.WINDOWLOG)

		# get most recent screen geometry and update active window
		self.updateWindowList()

	def updateWindowList(self):
		"""
		While updating unicode handling I noticed that getting the title from
		accessibility via app_title = kwargs['element']['AXTitle'] and getting
		if from app.localizedName() produce 2 different results. The first gives
		you a string with unicode characters all handled. The second gives you a
		unicode string that needs to be converted to ascii. Still trying to Figure
		out what to do.
		"""

		# get an early timestamp
		t = cfg.NOW()

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
			# bundle = app.bundleIdentifier() # unique for each app?
			active = app.isActive()
			pid = app.processIdentifier()
			d = {'name': name, 'active': active, 'windows':{}}
			self.apps_and_windows[int(pid)] = d # store app data by pid

			# get data for active window
			if active:
				mess = self.watched[pid]
				active_window = mess['AXFocusedWindow']['AXTitle']

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
				if name == active_window:
					active = True

				# unless it has a name and is on the top layer, we don't count it
				if owning_app_pid in self.apps_and_windows and window_layer == 0 and name:
					# add window data to the app_window dictionary
					window_dict = {'name': name, 'bounds': win_bounds, 'active': active}
					self.apps_and_windows[owning_app_pid]['windows'][window_id] = window_dict
			except:
				pass
				#raise

		# write self.apps_and_windows to a geometry file
		text = '{"time": ' + str(t) + ', "geometry": ' +  str(self.apps_and_windows) + "}"
		utils_cocoa.write_to_file(text, cfg.GEOLOG)

	### Computer sleep/wake callbacks ###
	def sleepCallback_(self, notification):
		t = cfg.NOW()
		text = '{"time": '+ str(t) + ' , "type": "Sleep"}'
		utils_cocoa.write_to_file(text, cfg.RECORDERLOG)

	def wakeCallback_(self, notification):
		t = cfg.NOW()
		text = '{"time": '+ str(t) + ' , "type": "Wake"}'
		utils_cocoa.write_to_file(text, cfg.RECORDERLOG)

		self.updateWindowList()

	def start_app_observers(self):
        # prompt user to grant accessibility access to Traces
		acc.is_enabled()

		# get an early timestamp
		t = cfg.NOW()

        # get workspace and list of all applications
		workspace = NSWorkspace.sharedWorkspace()
		activeApps = workspace.runningApplications()

		# listen for application events
		nc = workspace.notificationCenter()
		s = objc.selector(self.appLaunchCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidLaunchApplicationNotification', None)
		s = objc.selector(self.appTerminateCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidTerminateApplicationNotification', None)
		s = objc.selector(self.appActivateCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidActivateApplicationNotification', None)
		s = objc.selector(self.appDeactivateCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidDeactivateApplicationNotification', None)
		s = objc.selector(self.appHideCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidHideApplicationNotification', None)
		s = objc.selector(self.appUnhideCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidUnhideApplicationNotification', None)

        # track computer sleep events
		s = objc.selector(self.wakeCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceDidWakeNotification', None)
		s = objc.selector(self.sleepCallback_,signature='v@:@')
		nc.addObserver_selector_name_object_(self, s, 'NSWorkspaceWillSleepNotification', None)

		# other events that may be useful
        # https://developer.apple.com/library/mac/documentation/Cocoa/Reference/ApplicationKit/Classes/NSWorkspace_Class/
        # NSWorkspaceActiveSpaceDidChangeNotification
        # NSWorkspaceWillPowerOffNotification
        # NSWorkspaceDidPerformFileOperationNotification

        # prune list of applications to apps that appear in the dock
		regularApps = []
		for app in activeApps:
			if app.activationPolicy() == 0:
				regularApps.append(app)

        # listen for window events of these applications
		for app in regularApps:
			try:
				p = int(app.processIdentifier())
				name = utils_cocoa.ascii_encode(app.localizedName())
				mess = acc.create_application_ref(pid=p)
				mess.set_callback(self.windowCallback)
				mess.watch("AXMoved", "AXWindowResized", "AXFocusedWindowChanged",
							"AXWindowCreated","AXWindowMiniaturized",
							"AXWindowDeminiaturized") # AXMainWindowChanged
				# need to maintain the 'mess' object otherwise the listener
				# will be deleted on cleanup
				self.watched[p] = mess

				# log that the app is open
				text = '{"time": '+ str(t) + ' , "type": "Launch: Recording Started", "app": "' + name + '"}'
				utils_cocoa.write_to_file(text, cfg.APPLOG)

				#TODO may not need this logging here if we can save the information
				# while calling updateWindowList()
				if app.isActive():
					# log that application is active
					text = '{"time": '+ str(t) + ' , "type": "Activate", "app": "' + name + '"}'
					utils_cocoa.write_to_file(text, cfg.APPLOG)

					# # get information from frontmost window
					# title = mess['AXFocusedWindow']['AXTitle']
					# position = str(mess['AXFocusedWindow']['AXPosition'])
					# size = str(mess['AXFocusedWindow']['AXSize'])
					#
					# # log that frontmost window of active app is active
					# text = '{"time": ' + str(t) + ' , "type": "Activate", "app": "' + app.localizedName() + '", "window": "' + title + '", "position": ' + position + ' , "size": ' + size +' }'
					# utils_cocoa.write_to_file(text, cfg.WINDOWLOG)

			except:
				raise
				print "Could not register event listener for: " + str(name)

		# get inital list of windows and add window listeners
		self.updateWindowList()

		# start event loop to track events from other applications
		CFRunLoopRun()

	def stop_app_observers(self):
		t = cfg.NOW()

        # get workspace and list of all applications
		workspace = NSWorkspace.sharedWorkspace()
		activeApps = workspace.runningApplications()

		# let app observers be garabage collected
		self.watched = {}

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

			#TODO Traces is active on close. Figure out how to track last app deactivate event
			if app.isActive():
				# log that application is active
				text = '{"time": '+ str(t) + ' , "type": "Deactivate", "app": "' + name + '"}'
				utils_cocoa.write_to_file(text, cfg.APPLOG)

				# # get information from frontmost window
				# title = mess['AXFocusedWindow']['AXTitle']
				# position = str(mess['AXFocusedWindow']['AXPosition'])
				# size = str(mess['AXFocusedWindow']['AXSize'])
				#
				# # log that frontmost window of active app is active
				# text = '{"time": ' + str(t) + ' , "type": "Deactivate", "app": "' + name + '", "window": "' + title + '", "position": ' + position + ' , "size": ' + size +' }'
				# utils_cocoa.write_to_file(text, cfg.WINDOWLOG)
