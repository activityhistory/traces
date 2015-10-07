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
		self.sniffer = sniffer
		self.watched = {}
		self.apps = []
		self.apps_and_windows = {}

	### Application event callbacks ###
	def appLaunchCallback_(self, notification):
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		if app.activationPolicy() == 0:
			p = int(app.processIdentifier())
			mess = acc.create_application_ref(pid = p )
			mess.set_callback(self.windowCallback)
			mess.watch("AXMoved", "AXWindowResized", "AXFocusedWindowChanged",
						"AXWindowCreated","AXWindowMiniaturized",
						"AXWindowDeminiaturized")
			self.watched[p] = mess

			text = '{"time": '+ str(t) + ' , "type": "Launch", "app": "' + app.localizedName() + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		self.updateWindowList()

	def appTerminateCallback_(self, notification):
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		p = int(app.processIdentifier())
		if p in self.watched.keys():
			watcher = self.watched[p]
			del self.watched[p]

			text = '{"time": '+ str(t) + ' , "type": "Terminate", "app": "' + app.localizedName() + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		self.updateWindowList()

	def appActivateCallback_(self, notification):
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		p = int(app.processIdentifier())
		if p in self.watched.keys():
			text = '{"time": '+ str(t) + ' , "type": "Activate", "app": "' + app.localizedName() + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		self.updateWindowList()

	def appDeactivateCallback_(self, notification):
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		p = int(app.processIdentifier())
		if p in self.watched.keys():
			text = '{"time": '+ str(t) + ' , "type": "Deactivate", "app": "' + app.localizedName() + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

	def appHideCallback_(self, notification):
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		p = int(app.processIdentifier())
		if p in self.watched.keys():
			text = '{"time": '+ str(t) + ' , "type": "Hide", "app": "' + app.localizedName() + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		self.updateWindowList()

	def appUnhideCallback_(self, notification):
		t = cfg.NOW()
		app = notification.userInfo()["NSWorkspaceApplicationKey"]
		p = int(app.processIdentifier())
		if p in self.watched.keys():
			text = '{"time": '+ str(t) + ' , "type": "Unhide", "app": "' + app.localizedName() + '"}'
			utils_cocoa.write_to_file(text, cfg.APPLOG)

		self.updateWindowList()

	### Window event callbacks ###
	def windowCallback(self, **kwargs):
		t = cfg.NOW()
		notification_type = kwargs['notification']
		# remove 'AX' from front of event names before we save that info
		notification_title = str(kwargs['notification'])[2:-1]

		# when miniaturized, we may not be able to get window title and position data
		if notification_type == "AXWindowMiniaturized":
			app_title = kwargs['element']['AXTitle']
			text = '{"time": '+ str(t) + ' , "type": "' + notification_title + '", "app": "' + app_title + '" }'
			utils_cocoa.write_to_file(text, cfg.WINDOWLOG)

		# all other events should let us get title and postiion data
		else:
			# get the relevant data
			app_title = kwargs['element']['AXTitle']
			title = kwargs['element']['AXFocusedWindow']['AXTitle']
			position = str(kwargs['element']['AXFocusedWindow']['AXPosition'])
			size = str(kwargs['element']['AXFocusedWindow']['AXSize'])

			# write to window log file about event
			text = '{"time": ' + str(t) + ' , "type": "' + notification_title + '", "app": "' + app_title + '", "window": "' + title + '", "position": ' + position + ' , "size": ' + size +' }'
			utils_cocoa.write_to_file(text, cfg.WINDOWLOG)

		# get most recent screen geometry after the change
		self.updateWindowList()

	def updateWindowList(self):
		# get a timestamp at the start of call
		t = cfg.NOW()
		#TODO do I want to recreate this list each time a window event occurs
		# or do I want to compare a new list to the old list?
		self.apps_and_windows = {}

		# get list of applications that show up in the dock
		workspace = NSWorkspace.sharedWorkspace()
		activeApps = workspace.runningApplications()
		regularApps = []
		for app in activeApps:
			if app.activationPolicy() == 0:
				regularApps.append(app)

		# save app info to dictionary
		# may also want to transform the text to unicode
		for app in regularApps:
			name = app.localizedName()
			bundle = app.bundleIdentifier() # unique for each app?
			active = app.isActive()
			pid = app.processIdentifier()
			d = {'name': name, 'bundle': bundle, 'active': active, 'windows':{}}
			# store app data by pid
			# note that pids are not consistent (e.g. while an application will
			# have the same pid whenever it is queried during a session, it will
			# not necissarily have the same pid across sessions)
			self.apps_and_windows[int(pid)] = d

			if active:
				if pid in self.watched.keys():
					# log that application is active
					text = '{"time": '+ str(t) + ' , "type": "Activate", "app": "' + app.localizedName() + '"}'
					utils_cocoa.write_to_file(text, cfg.APPLOG)

					# log information of focused window
					title = self.watched[pid]['AXFocusedWindow']['AXTitle']
					position = str(self.watched[pid]['AXFocusedWindow']['AXPosition'])
					size = str(self.watched[pid]['AXFocusedWindow']['AXSize'])

					text = '{"time": ' + str(t) + ' , "type": "Activate", "app": "' + app.localizedName() + '", "window": "' + title + '", "position": ' + position + ' , "size": ' + size +' }'
					utils_cocoa.write_to_file(text, cfg.WINDOWLOG)

		# add list of current windows
		options = kCGWindowListOptionAll + kCGWindowListExcludeDesktopElements
		windows = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
		for window in windows:
			try:
				owning_app_pid = window['kCGWindowOwnerPID']
				window_layer = window['kCGWindowLayer']
				name = window['kCGWindowName']
				window_id = window['kCGWindowNumber']
				bounds = window['kCGWindowBounds']
				win_bounds = {'width':bounds['Width'], 'height':bounds['Height'], 'x':bounds['X'], 'y':bounds['Y']}
				# unless it has a name and is on the top layer, we don't count it
				if owning_app_pid in self.apps and window_layer ==0 and name:
					window_dict = {'name': name, 'bounds': win_bounds}
					self.apps_and_windows[owning_app_pid]['windows'][window_id] = window_dict
			except:
				pass

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
				mess = acc.create_application_ref(pid=p)
				mess.set_callback(self.windowCallback)
				mess.watch("AXMoved", "AXWindowResized", "AXFocusedWindowChanged",
							"AXWindowCreated","AXWindowMiniaturized",
							"AXWindowDeminiaturized") # AXMainWindowChanged
				# need to maintain the 'mess' object otherwise the listener
				# will be deleted on cleanup
				self.watched[p] = mess
				self.apps.append(p)

				# log that the app is open
				text = '{"time": '+ str(t) + ' , "type": "Launch: Recording Started", "app": "' + app.localizedName() + '"}'
				utils_cocoa.write_to_file(text, cfg.APPLOG)

				#TODO may not need this logging here if we can save the information
				# while calling updateWindowList()
				# if app.isActive():
				# 	# log that application is active
				# 	f = open(appfile, 'a')
				# 	text = '{"time": '+ str(t) + ' , "type": "Activate", "app": "' + app.localizedName() + '"}'
				# 	print >>f, text
				# 	f.close()
				#
				# 	# get information from frontmost window
				# 	title = mess['AXFocusedWindow']['AXTitle']
				# 	position = str(mess['AXFocusedWindow']['AXPosition'])
				# 	size = str(mess['AXFocusedWindow']['AXSize'])
				#
				# 	# log that frontmost window of active app is active
				# 	winfile = os.path.join(os.path.expanduser(cfg.CURRENT_DIR), cfg.WINDOWLOG)
				# 	f = open(winfile, 'a')
				# 	text = '{"time": ' + str(t) + ' , "type": "Activate", "app": "' + app.localizedName() + '", "window": "' + title + '", "position": ' + position + ' , "size": ' + size +' }'
				# 	print >>f, text
				# 	f.close()

			except:
				print "Could not register event listener for: " + str(app.localizedName())

		# get inital list of windows
		self.updateWindowList()

		# start event loop to track events from other applications
		CFRunLoopRun()

# My First attempt to track accessibility with Pyobjc bindings
# Opted to use third party accessiblity module instead

# from HIServices import (AXObserverCreate, AXObserverRef,
#                         AXObserverAddNotification, kAXWindowMovedNotification,
#                         kAXWindowCreatedNotification, kAXWindowResizedNotification,
#                         kAXApplicationActivatedNotification, kAXApplicationHiddenNotification,
#                         kAXMainWindowAttribute, AXUIElementCopyAttributeValue,
#                         AXUIElementCreateApplication, NSRunLoop,
#                         AXObserverGetRunLoopSource, kCFRunLoopDefaultMode)

# @objc.callbackFor(AXObserverCreate)
# def myCallback(obs, element, notification, contextdata):
#     print "The application moved, a window was created, or resized"

# def update_app_observers():
#
#     @objc.callbackFor(AXObserverCreate)
#     def myCallback(obs, element, notification, contextdata):
#         print "The application moved, a window was created, or resized"
#
#     # get list of all applications
#     workspace = NSWorkspace.sharedWorkspace()
#     activeApps = workspace.runningApplications()
#
#     # prune list to regular apps that appear in the dock
#     regularApps = []
#     for app in activeApps:
#         if app.activationPolicy() == 0:
#             regularApps.append(app)
#
#     observers = []
#
#     # create osbervers for events thrown by these apps
#     for app in regularApps:
#         # create observer
#         pid = app.processIdentifier()
#         err, obser = AXObserverCreate(pid, myCallback, None)
#         # print "Observer context is " + str(CFRunLoopObserverGetContext(obser, None))
#
#         # if we have an observer, add it to the run loop
#         if err == 0:
#             CFRunLoopAddSource(CFRunLoopGetCurrent(), AXObserverGetRunLoopSource(obser), kCFRunLoopDefaultMode)
#             # and listen for certain events
#             axapp = AXUIElementCreateApplication(pid)
#
#             #TODO why is the "retrieved context not valid"?
#             # it seems like the callback is not linked correctly because the context for
#             # this source points to a callback of 0x0 which I think is the null pointer
#             # print "Run Loop context: " + str(CFRunLoopSourceGetContext(AXObserverGetRunLoopSource(obser), None))
#             # print "Run Loop is valid: " + str(CFRunLoopSourceIsValid(AXObserverGetRunLoopSource(obser))) + " for " + str(AXObserverGetRunLoopSource(obser))
#
#             err1 = AXObserverAddNotification(obser, axapp, kAXApplicationActivatedNotification, None)
#             if err1 == 0:
#                 observers.append({pid: obser})
#             else:
#                 print "Failed to link notifications to observer for " + str(app.localizedName()) + " error is " + str(err1)
#
#         else:
#             print "Error with creating accessibility observer for " + str(app.localizedName()) + " " + str(err)


	# hold handling of apps

    # def handler(self, event):
    #
    #             chromeChecked = False
    #             safariChecked = False
    #             for window in windowList:
    #                 window_name = str(window.get('kCGWindowName', u'').encode('ascii', 'replace'))
    #                 owner = window['kCGWindowOwnerName']
    #                 url = 'NO_URL'
    #                 geometry = window['kCGWindowBounds']
    #                 windows_to_ignore = ["Focus Proxy", "Clipboard"]
    #                 for app in regularApps:
    #                     if app.localizedName() == owner:
    #                         if (window_name and window_name not in windows_to_ignore):
    #                             if owner == 'Google Chrome' and not chromeChecked:
    #                                 s = NSAppleScript.alloc().initWithSource_("tell application \"Google Chrome\" \n set tabs_info to {} \n set window_list to every window \n repeat with win in window_list \n set tab_list to tabs in win \n repeat with t in tab_list \n set the_title to the title of t \n set the_url to the URL of t \n set the_bounds to the bounds of win \n set t_info to {the_title, the_url, the_bounds} \n set end of tabs_info to t_info \n end repeat \n end repeat \n return tabs_info \n end tell")
    #                                 tabs_info = s.executeAndReturnError_(None)
    #                                 # Applescript returns list of lists including title and url in NSAppleEventDescriptors
    #                                 # https://developer.apple.com/library/mac/Documentation/Cocoa/Reference/Foundation/Classes/NSAppleEventDescriptor_Class/index.html
    #                                 if tabs_info[0]:
    #                                     numItems = tabs_info[0].numberOfItems()
    #                                     for i in range(1, numItems+1):
    #                                         window_name = str(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(1).stringValue().encode('ascii', 'replace'))
    #                                         if window_name:
    #                                             url = str(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(2 ).stringValue())
    #                                         else:
    #                                             url = "NO_URL"
    #                                         x1 = int(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(3).descriptorAtIndex_(1).stringValue())
    #                                         y1 = int(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(3).descriptorAtIndex_(2).stringValue())
    #                                         x2 = int(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(3).descriptorAtIndex_(3).stringValue())
    #                                         y2 = int(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(3).descriptorAtIndex_(4).stringValue())
    #                                         regularWindows.append({'process': 'Google Chrome', 'title': window_name, 'url': url, 'geometry': {'X':x1,'Y':y1,'Width':x2-x1,'Height':y2-y1} })
    #                                     chromeChecked = True
    #                             elif owner == 'Safari' and not safariChecked:
    #                                 s = NSAppleScript.alloc().initWithSource_("tell application \"Safari\" \n set tabs_info to {} \n set winlist to every window \n repeat with win in winlist \n set ok to true \n try \n set tablist to every tab of win \n on error errmsg \n set ok to false \n end try \n if ok then \n repeat with t in tablist \n set thetitle to the name of t \n set theurl to the URL of t \n set thebounds to the bounds of win \n set t_info to {thetitle, theurl, thebounds} \n set end of tabs_info to t_info \n end repeat \n end if \n end repeat \n return tabs_info \n end tell")
    #                                 tabs_info = s.executeAndReturnError_(None)
    #                                 if tabs_info[0]:
    #                                     numItems = tabs_info[0].numberOfItems()
    #                                     for i in range(1, numItems+1):
    #                                         window_name = str(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(1).stringValue().encode('ascii', 'replace'))
    #                                         if window_name:
    #                                             url = str(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(2 ).stringValue())
    #                                         else:
    #                                             url = "NO_URL"
    #                                         x1 = int(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(3).descriptorAtIndex_(1).stringValue())
    #                                         y1 = int(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(3).descriptorAtIndex_(2).stringValue())
    #                                         x2 = int(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(3).descriptorAtIndex_(3).stringValue())
    #                                         y2 = int(tabs_info[0].descriptorAtIndex_(i).descriptorAtIndex_(3).descriptorAtIndex_(4).stringValue())
    #                                         regularWindows.append({'process': 'Safari', 'title': window_name, 'url': url, 'geometry': {'X':x1,'Y':y1,'Width':x2-x1,'Height':y2-y1} })
    #                             else:
    #                                 regularWindows.append({'process': owner, 'title': window_name, 'url': url, 'geometry': geometry})
    #
    #
    #             # get active app, window, url and geometry
    #             # only track for regular apps

    #             for app in regularApps:
    #                 if app.isActive():
    #                     for window in windowList:
    #                         if (window['kCGWindowNumber'] == event.windowNumber() or (not event.windowNumber() and window['kCGWindowOwnerName'] == app.localizedName())):
    #                             geometry = window['kCGWindowBounds']
    #
    #                             # get browser_url
    #                             browser_url = 'NO_URL'
    #                             if len(window.get('kCGWindowName', u'').encode('ascii', 'replace')) > 0:
    #                                 if (window.get('kCGWindowOwnerName') == 'Google Chrome'):
    #                                     s = NSAppleScript.alloc().initWithSource_("tell application \"Google Chrome\" \n return URL of active tab of front window as string \n end tell")
    #                                     browser_url = s.executeAndReturnError_(None)
    #                                 if (window.get('kCGWindowOwnerName') == 'Safari'):
    #                                     s = NSAppleScript.alloc().initWithSource_("tell application \"Safari\" \n set theURL to URL of current tab of window 1 \n end tell")
    #                                     browser_url = s.executeAndReturnError_(None)
    #                                 browser_url = str(browser_url[0])[33:-3]
    #
