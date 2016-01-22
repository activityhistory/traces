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


import objc
from objc import IBAction, IBOutlet

from AppKit import *
from Foundation import *

from Cocoa import NSNotificationCenter


def getValueForPreference(pref):
	"""
	Finds the value for a preference in the defaults controller and returns it
	The defaults controller lets us save preferences across runnings of the program
	"""
	try:
		value = NSUserDefaultsController.sharedUserDefaultsController().values().valueForKey_(pref)
		return value
	except:
		print "Error retrieving preference value"
		return

def setInitialPreferenceValues():
	# set preferance defaults for user-facing preferences
	prefDictionary = {}
	prefDictionary[u"screenshots"] = True
	prefDictionary[u'imageSize'] = 720					# in px
	prefDictionary[u"periodicScreenshots"] = True
	prefDictionary[u"imagePeriodicFrequency"] = 60		# in s
	prefDictionary[u"eventScreenshots"] = True
	prefDictionary[u"imageTimeMin"] = 100			   # in ms
	prefDictionary[u"imageTimeMax"] = 1000			   # in ms
	prefDictionary[u"keystrokes"] = True
	prefDictionary[u"experienceLoop"] = True
	prefDictionary[u"experienceTime"] = 1800			# in s
	prefDictionary[u"recording"] = True
	NSUserDefaultsController.sharedUserDefaultsController().setInitialValues_(prefDictionary)

# Preferences window controller
class PreferencesController(NSWindowController):

	# outlets for UI elements
	screenshotSizePopup = IBOutlet()
	screenshotSizeMenu = IBOutlet()
	clearDataPopup = IBOutlet()

	sniffer = None

	# handle changes to the preferences
	@IBAction
	def changeScreenshot_(self,sender):
		screenshots = getValueForPreference('screenshots')
		periodic = getValueForPreference('periodicScreenshots')
		if screenshots and periodic:
			self.sniffer.activity_tracker.startLoops()
		elif not screenshots or not periodic:
			self.sniffer.activity_tracker.stopLoops()

	@IBAction
	def changePeriodicScreenshots_(self,sender):
		periodic = getValueForPreference('periodicScreenshots')
		if periodic:
			self.sniffer.activity_tracker.startLoops()
		else:
			self.sniffer.activity_tracker.stopLoops()

	@IBAction
	def changePeriodicRate_(self,sender):
		self.sniffer.activity_tracker.restartScreenshotLoop()

	@IBAction
	def changeKeystrokeRecording_(self,sender):
		print "You asked us to start/stop keystroke recording"

	@IBAction
	def changeBookmark_(self,sender):
		print "You asked us to start/stop periodic bookmarking"

	@IBAction
	def changeBookmarkRate_(self,sender):
		print "You asked us to change the bookmark rate"

	@IBAction
	def clearData_(self,sender):
		self.sniffer.activity_tracker.clearData()

	def windowDidLoad(self):
		NSWindowController.windowDidLoad(self)

		# Set screenshot size options based on screen's native height
		self.prefController.screenshotSizeMenu.removeAllItems()
		nativeHeight = int(NSScreen.mainScreen().frame().size.height)
		menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(str(nativeHeight)+' px', '', '')
		menuitem.setTag_(nativeHeight)
		self.prefController.screenshotSizeMenu.addItem_(menuitem)

		sizes = [1080,720,480]
		for x in sizes:
			if x < nativeHeight:
				menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(str(x)+' px', '', '')
				menuitem.setTag_(x)
				self.prefController.screenshotSizeMenu.addItem_(menuitem)

		# update newly created screenshot size dropdown to select saved preference or default size
		selectedSize = NSUserDefaultsController.sharedUserDefaultsController().values().valueForKey_('imageSize')
		selectedMenuItem = self.prefController.screenshotSizeMenu.itemWithTag_(selectedSize)
		if(selectedMenuItem):
			self.prefController.screenshotSizePopup.selectItemWithTag_(selectedSize)
		else:
			nativeMenuItem = self.prefController.screenshotSizeMenu.itemWithTag_(nativeHeight)
			NSUserDefaultsController.sharedUserDefaultsController().defaults().setInteger_forKey_(nativeHeight,'imageSize')
			self.prefController.screenshotSizePopup.selectItemWithTag_(nativeHeight)

	def show(self, sniffer):
		try:
			if self.prefController:
				self.prefController.close()
		except:
			pass

		self.sniffer = sniffer

		# open window from NIB file, show front and center
		self.prefController = PreferencesController.alloc().initWithWindowNibName_("preferences")
		self.prefController.showWindow_(None)
		self.prefController.window().makeKeyAndOrderFront_(None)
		self.prefController.window().center()
		self.prefController.retain()


		# NSNotificationCenter.defaultCenter().postNotificationName_object_('makeAppActive',self)

		self.sniffer.app.activateIgnoringOtherApps_(True)

		# make window close on Cmd-w
		self.prefController.window().standardWindowButton_(NSWindowCloseButton).setKeyEquivalentModifierMask_(NSCommandKeyMask)
		self.prefController.window().standardWindowButton_(NSWindowCloseButton).setKeyEquivalent_("w")

		return self.prefController

	show = classmethod(show)
