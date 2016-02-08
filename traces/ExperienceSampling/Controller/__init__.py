# -*- coding: utf-8 -*-

from Cocoa import *
from Foundation import NSObject
from maincontroller import MainController
from appdelegate import AppDelegate

def init():
	app = NSApplication.sharedApplication()
	NSApp.activateIgnoringOtherApps_(True)

def run():
	main = MainController.alloc().initWithWindowNibName_('Main')
	main.showWindow_(main)

	from PyObjCTools import AppHelper
	AppHelper.runEventLoop()