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
import errno
import threading

from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper
import LaunchServices
from Cocoa import (NSEvent, NSScreen, NSURL, NSString)
import Quartz
from Quartz import (CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly,
                    kCGWindowListOptionAll, kCGWindowListExcludeDesktopElements,
                    kCGNullWindowID, CGImageGetHeight, CGImageGetWidth,
                    CFRunLoopRun)
import Quartz.CoreGraphics as CG

import config as cfg
import preferences
import utils_cocoa

from recorders.app_recorder import AppRecorder
from recorders.click_recorder import ClickRecorder
from recorders.key_recorder import KeyRecorder
from recorders.move_recorder import MoveRecorder
from recorders.scroll_recorder import ScrollRecorder

from experience import ExperienceController


class Sniffer:
    def __init__(self, activity_tracker):
        # set reference to tracker object that spawned this sniffer
        self.activity_tracker = activity_tracker
        self.delegate = None

    def createAppDelegate(self):
        sc = self

        class AppDelegate(NSObject):
            """
            The delegate recieves messages from outside the application ( such
            as to quit the application) and handles them.
            """
            def __init__(self):
                self.statusbar = None
                self.state = 'pause'
                self.screenshot = True
                self.recordingAudio = False
                # self.activity_tracer = None

            def applicationDidFinishLaunching_(self, notification):
                print "Traces finished launching..."

                # save recorder turned on event
                t = cfg.NOW()

                text = '{"time": '+ str(t) + ' , "type": "Start Traces"}'
                utils_cocoa.write_to_file(text, cfg.RECORDERLOG)

                # set inital values for the preferences
                preferences.setInitialPreferenceValues()

                # create status-bar drop-down menu
                self.createStatusMenu()

                # start loops to take screenshots and parse log files
                self.activity_tracker.checkLoops()

            def applicationWillTerminate_(self, application):
                t = cfg.NOW()

                # close all open app and window listeners
                sc.ar.stop_app_observers()

                # save recorder turned off event
                text = '{"time": '+ str(t) + ' , "type": "Exit Traces"}'
                utils_cocoa.write_to_file(text, cfg.RECORDERLOG)

                #TODO tell application to parse logs one last time before quiting
                sc.activity_tracker.storage.parseToSqlite()
                sc.activity_tracker.storage.sqlcommit()

                print "Exiting Traces..."
                sc.cancel()

            def toggleLogging_(self, notification):
                print "Toggle Recording"

                recording = preferences.getValueForPreference('recording')
                recording = not recording
                NSUserDefaultsController.sharedUserDefaultsController().defaults().setBool_forKey_(recording,'recording')

                self.activity_tracker.checkLoops()

                #change text and enabled status of screenshot menu item
                if recording:
                  self.loggingMenuItem.setTitle_("Pause Recording")
                else:
                  self.loggingMenuItem.setTitle_("Start Recording")
                self.changeIcon()

            def changeIcon(self):
                record = preferences.getValueForPreference('recording')
                if(record):
                    self.statusitem.setImage_(self.icon)
                else:
                    self.statusitem.setImage_(self.iconGray)

            def showPreferences_(self, notification):
                NSLog("Showing Preference Window...")
                prefContr = preferences.PreferencesController.show()
                prefContr.sniffer = sc

                # needed to show window on top of other applications
                sc.app.activateIgnoringOtherApps_(True)

            def showExperience_(self, notification):
                print "Showing Experience Sampling Window on Request..."
                ExperienceController.show(sc)

            # could possibly do this in XCode, but creating by code works too
            def createStatusMenu(self):
                print "Creating app menu"
                statusbar = NSStatusBar.systemStatusBar()

                # Create the statusbar item
                self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
                # self.statusitem.setTitle_(u"Selfspy")

                # Load all images
                self.icon = NSImage.alloc().initByReferencingFile_('../Resources/clock.png')
                self.icon.setScalesWhenResized_(True)
                self.size_ = self.icon.setSize_((20, 20))
                self.statusitem.setImage_(self.icon)

                self.iconGray = NSImage.alloc().initByReferencingFile_('../Resources/clock_grey.png')
                self.iconGray.setScalesWhenResized_(True)
                self.iconGray.setSize_((20, 20))

                self.changeIcon()

                # Let it highlight upon clicking
                self.statusitem.setHighlightMode_(1)
                # Set a tooltip
                self.statusitem.setToolTip_('Traces')

                # Build a very simple menu
                self.menu = NSMenu.alloc().init()
                self.menu.setAutoenablesItems_(False)

                if NSUserDefaultsController.sharedUserDefaultsController().values().valueForKey_('recording'):
                    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Pause Recording', 'toggleLogging:', '')
                else:
                    menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Start Recording', 'toggleLogging:', '')
                #menuitem.setEnabled_(False)
                self.menu.addItem_(menuitem)
                self.loggingMenuItem = menuitem

                menuitem = NSMenuItem.separatorItem()
                self.menu.addItem_(menuitem)

                menuitem = NSMenuItem.separatorItem()
                self.menu.addItem_(menuitem)

                menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Preferences...', 'showPreferences:', '')
                self.menu.addItem_(menuitem)

                menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Leave a message', 'showExperience:', '')
                self.menu.addItem_(menuitem)

                menuitem = NSMenuItem.separatorItem()
                self.menu.addItem_(menuitem)

                menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit Traces', 'terminate:', '')
                self.menu.addItem_(menuitem)

                # Bind it to the status item
                self.statusitem.setMenu_(self.menu)

                self.statusitem.setEnabled_(TRUE)
                self.statusitem.retain()

        return AppDelegate

    def run(self):
        # set up the application
        self.app = NSApplication.sharedApplication()
        self.delegate = self.createAppDelegate().alloc().init()
        self.delegate.activity_tracker = self.activity_tracker
        self.app.setDelegate_(self.delegate)
        self.app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        self.workspace = NSWorkspace.sharedWorkspace()

        # start listeners for event recorders
        self.cr = ClickRecorder(self)
        self.cr.start_click_listener()
        self.kr = KeyRecorder(self)
        self.kr.start_key_listener()
        self.mr = MoveRecorder(self)
        self.mr.start_move_listener()
        self.sr = ScrollRecorder(self)
        self.sr.start_scroll_listener()

        # I can get this to work, but it blocks the rest of the code from executing
        # app recording needs a separate thread to listen for events on
        self.ar = AppRecorder(self)
        self.art = threading.Thread(target=self.ar.start_app_observers)
        self.art.start()

        # run the Traces application
        AppHelper.runEventLoop()

    def cancel(self):
        AppHelper.stopEventLoop()

    #https://pythonhosted.org/pyobjc/examples/Quartz/Core%20Graphics/CGRotation/index.html
    def screenshot(self, path, region = None):
      try:
        # Set to capture entire screen, including multiple monitors
        if region is None:
          region = CG.CGRectInfinite

        # Create CGImage, composite image of windows in region
        image = CG.CGWindowListCreateImage(
          region,
          CG.kCGWindowListOptionOnScreenOnly,
          CG.kCGNullWindowID,
          CG.kCGWindowImageDefault
        )

        scr = NSScreen.screens()
        xmin = 0
        ymin = 0
        for s in scr:
            if s.frame().origin.x < xmin:
                xmin = s.frame().origin.x
            if s.frame().origin.y < ymin:
                ymin = s.frame().origin.y

        nativeHeight = CGImageGetHeight(image)*1.0
        nativeWidth = CGImageGetWidth(image)*1.0
        nativeRatio = nativeWidth/nativeHeight

        prefHeight = NSUserDefaultsController.sharedUserDefaultsController().values().valueForKey_('imageSize')
        height = int(prefHeight/scr[0].frame().size.height*nativeHeight)
        width = int(nativeRatio * height)
        heightScaleFactor = height/nativeHeight
        widthScaleFactor = width/nativeWidth

        mouseLoc = NSEvent.mouseLocation()
        x = int(mouseLoc.x)
        y = int(mouseLoc.y)
        w = 16
        h = 24
        scale_x = int((x-xmin) * widthScaleFactor)
        scale_y = int((y-h+5-ymin) * heightScaleFactor)
        scale_w = w*widthScaleFactor
        scale_h = h*heightScaleFactor

        #Allocate image data and create context for drawing image
        imageData = LaunchServices.objc.allocateBuffer(int(4 * width * height))
        bitmapContext = Quartz.CGBitmapContextCreate(
          imageData, # image data we just allocated...
          width,
          height,
          8, # 8 bits per component
          4 * width, # bytes per pixel times number of pixels wide
          Quartz.CGImageGetColorSpace(image), # use the same colorspace as the original image
          Quartz.kCGImageAlphaPremultipliedFirst # use premultiplied alpha
        )

        #Draw image on context at new scale
        rect = CG.CGRectMake(0.0,0.0,width,height)
        Quartz.CGContextDrawImage(bitmapContext, rect, image)

        # Add Mouse cursor to the screenshot
        cursorPath = "../Resources/cursor.png"
        cursorPathStr = NSString.stringByExpandingTildeInPath(cursorPath)
        cursorURL = NSURL.fileURLWithPath_(cursorPathStr)

        # Create a CGImageSource object from 'url'.
        cursorImageSource = Quartz.CGImageSourceCreateWithURL(cursorURL, None)

        # Create a CGImage object from the first image in the file. Image
        # indexes are 0 based.
        cursorOverlay = Quartz.CGImageSourceCreateImageAtIndex(cursorImageSource, 0, None)

        Quartz.CGContextDrawImage(bitmapContext,
          CG.CGRectMake(scale_x, scale_y, scale_w, scale_h),
          cursorOverlay)

        #Recreate image from context
        imageOut = Quartz.CGBitmapContextCreateImage(bitmapContext)

        #Image properties dictionary
        dpi = 72 # FIXME: Should query this from somewhere, e.g for retina display
        properties = {
          Quartz.kCGImagePropertyDPIWidth: dpi,
          Quartz.kCGImagePropertyDPIHeight: dpi,
          Quartz.kCGImageDestinationLossyCompressionQuality: 0.6,
        }

        #Convert path to url for saving image
        pathWithCursor = path[0:-4] + "_" + str(x) + "_" + str(y) + '.jpg'
        pathStr = NSString.stringByExpandingTildeInPath(pathWithCursor)
        url = NSURL.fileURLWithPath_(pathStr)

        #Set image destination (where it will be saved)
        dest = Quartz.CGImageDestinationCreateWithURL(
          url,
          LaunchServices.kUTTypeJPEG, # file type
          1, # 1 image in file
          None
        )

        # Add the image to the destination, with certain properties
        Quartz.CGImageDestinationAddImage(dest, imageOut, properties)

        # finalize the CGImageDestination object.
        Quartz.CGImageDestinationFinalize(dest)

        #For testing how long it takes to take screenshot
        print 'took ' + str(height) + 'px screenshot'

      except KeyboardInterrupt:
        print "Keyboard interrupt"
        AppHelper.stopEventLoop()
      except errno.ENOSPC:
          print "No space left on storage device. Turning off Traces recording."
          self.delegate.toggleLogging_(self)
      except:
        print "Could not save image"

    def got_location_change(self, latitude, longitude, latitudeRange, longitudeRange):
        print "location_change", latitude, longitude
