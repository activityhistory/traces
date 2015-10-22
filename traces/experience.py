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

from Foundation import *
from AppKit import *

from Cocoa import NSCommandKeyMask

import config as cfg

from data.sqlite.models import Experience

# Experience Sampling window controller
class ExperienceController(NSWindowController):

    experienceText = IBOutlet()

    @IBAction
    #TODO implement saving of the text...
    def recordText_(self, sender):
        t = cfg.NOW()
        message = self.experienceText.stringValue()
        e = Experience(t, message)
        self.sniffer.activity_tracker.storage.session.add(e)
        self.sniffer.activity_tracker.storage.sqlcommit()

        print 'Received experience message of: ' + message
        self.expController.close()

    # override window close to track when users close the experience window
    def overrideClose(self):
        s = objc.selector(self.setIgnoredAndClose_,signature='v@:@')
        self.expController.window().standardWindowButton_(NSWindowCloseButton).setTarget_(self.expController)
        self.expController.window().standardWindowButton_(NSWindowCloseButton).setAction_(s)
        self.expController.window().standardWindowButton_(NSWindowCloseButton).setKeyEquivalentModifierMask_(NSCommandKeyMask)
        self.expController.window().standardWindowButton_(NSWindowCloseButton).setKeyEquivalent_("w")

    def setIgnoredAndClose_(self, notification):
        self.ignored = True
        NSNotificationCenter.defaultCenter().postNotificationName_object_('experienceReceived',self)
        self.expController.close()

    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)

    def show(self, sniffer):
        try:
            # close the window if its already open
            if self.expController.window().isVisible():
                self.expController.close()
        except:
            pass

        self.sniffer = sniffer

        # open window from NIB file, show front and center
        self.expController = ExperienceController.alloc().initWithWindowNibName_("experience")
        self.expController.showWindow_(None)
        self.expController.window().makeKeyAndOrderFront_(None)
        self.expController.window().center()
        self.expController.retain()

        # needed to show window on top of other applications
        # NSNotificationCenter.defaultCenter().postNotificationName_object_('makeAppActive',self)

        self.sniffer.app.activateIgnoringOtherApps_(True)

        self.overrideClose(self)

        return self.expController

    show = classmethod(show)
