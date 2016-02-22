# -*- coding: utf-8 -*-

from Cocoa import *
from Foundation import NSObject
from maincontroller import MainController

def init():
	# init the OS X application
	app = NSApplication.sharedApplication()
	NSApp.activateIgnoringOtherApps_(True)

def run():
	# loading MainController
	main = MainController.alloc().initWithWindowNibName_('Main')
	main.showWindow_(main)

	from PyObjCTools import AppHelper
	AppHelper.runEventLoop()